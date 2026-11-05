#!/usr/bin/env python3
"""Stream existing Docker Hub OCI into GHCR without rebuilding models.

Source reference is passed through OCI_SOURCE_IMAGE (GitHub Secret), never
printed. Original Python, Worker, Workflow and model *bytes* stay unchanged.
An oversized compressed source layer is carried as several GHCR-safe OCI
tar layers and restored at container startup before the original entrypoint.
"""
from __future__ import annotations
import base64
import copy
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request

BLOCK = 8 * 1024 * 1024
CHUNK = 3_000_000_000
LIMIT = 9_000_000_000
LAYER = "application/vnd.oci.image.layer.v1.tar+gzip"
MANIFEST = "application/vnd.oci.image.manifest.v1+json"
CONFIG = "application/vnd.oci.image.config.v1+json"
ACCEPT = ", ".join([MANIFEST, "application/vnd.docker.distribution.manifest.v2+json",
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json"])

def die(message):
    raise RuntimeError(message)

def digest(data):
    return "sha256:" + hashlib.sha256(data).hexdigest()

class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        nextreq = super().redirect_request(req, fp, code, msg, headers, newurl)
        if nextreq is not None and urllib.parse.urlsplit(req.full_url).hostname != urllib.parse.urlsplit(newurl).hostname:
            nextreq.remove_header("Authorization")
            nextreq.unredirected_hdrs.pop("Authorization", None)
        return nextreq

OPENER = urllib.request.build_opener(SafeRedirect())

def api(method, url, token=None, data=None, accept=None, extra=None, limit=3_000_000):
    hdr = dict(extra or {})
    if token: hdr["Authorization"] = "Bearer " + token
    if accept: hdr["Accept"] = accept
    if data is not None: hdr.setdefault("Content-Type", "application/octet-stream")
    req = urllib.request.Request(url, method=method, data=data, headers=hdr)
    try:
        with OPENER.open(req, timeout=100) as response:
            result = response.read(limit+1) if method=="GET" else b""
            if len(result) > limit: die("API_RESPONSE_TOO_LARGE")
            return response.status, dict(response.headers), result
    except urllib.error.HTTPError as exc:
        code, headers = exc.code, dict(exc.headers)
        exc.close()
        return code, headers, b""

def source_auth(reference):
    name = reference.removeprefix("docker.io/")
    if not re.fullmatch(r"[a-z0-9_-]+(?:/[a-z0-9_.-]+)+(?::[A-Za-z0-9_.-]+|@sha256:[0-9a-f]{64})", name):
        die("SOURCE_IMAGE_REFERENCE_INVALID")
    repo, tag = name.split("@",1) if "@" in name else name.rsplit(":",1)
    url="https://auth.docker.io/token?"+urllib.parse.urlencode({
        "service":"registry.docker.io","scope":f"repository:{repo}:pull"})
    code, _, result = api("GET",url)
    if code!=200: die("SOURCE_AUTH_FAILED")
    token=json.loads(result).get("token")
    if not token: die("SOURCE_TOKEN_MISSING")
    return repo, tag, token

def ghcr_auth(repository):
    actor=os.getenv("GITHUB_ACTOR","")
    ghkey=os.getenv("GITHUB_TOKEN","")
    if not actor or not ghkey: die("GHCR_GITHUB_TOKEN_MISSING")
    basic=base64.b64encode((actor+":"+ghkey).encode()).decode()
    url="https://ghcr.io/token?"+urllib.parse.urlencode({
        "service":"ghcr.io","scope":f"repository:{repository}:pull,push"})
    code, _, raw=api("GET",url,extra={"Authorization":"Basic "+basic})
    if code!=200: die("GHCR_BEARER_HTTP_"+str(code))
    token=json.loads(raw).get("token")
    if not token: die("GHCR_BEARER_MISSING")
    return token

def source_manifest(repo, tag, token):
    base=f"https://registry-1.docker.io/v2/{repo}"
    code, _, raw=api("GET",base+"/manifests/"+tag,token,accept=ACCEPT)
    if code!=200: die("SOURCE_MANIFEST_UNAVAILABLE")
    obj=json.loads(raw)
    if "manifests" in obj:
        matches=[x for x in obj["manifests"] if x.get("platform",{}).get("os")=="linux" and x.get("platform",{}).get("architecture")=="amd64"]
        if len(matches)!=1: die("SOURCE_PLATFORM_UNAVAILABLE")
        code, _, raw=api("GET",base+"/manifests/"+matches[0]["digest"],token,accept=ACCEPT)
        if code!=200 or digest(raw)!=matches[0]["digest"]: die("SOURCE_MANIFEST_DIGEST_MISMATCH")
        obj=json.loads(raw)
    if "config" not in obj or not obj.get("layers"): die("SOURCE_MANIFEST_INVALID")
    return obj

def source_stream(repo, sha, token):
    req=urllib.request.Request(
        f"https://registry-1.docker.io/v2/{repo}/blobs/{sha}",
        headers={"Authorization":"Bearer "+token})
    return OPENER.open(req,timeout=180)

def download_verified(repo, desc, token, output):
    h=hashlib.sha256()
    count=0
    with source_stream(repo,desc["digest"],token) as inp,open(output,"wb") as out:
        while True:
            piece=inp.read(BLOCK)
            if not piece: break
            count+=len(piece)
            if count>=LIMIT: die("SOURCE_LAYER_OVER_LIMIT")
            h.update(piece)
            out.write(piece)
    if count!=desc["size"] or "sha256:"+h.hexdigest()!=desc["digest"]:
        die("SOURCE_BLOB_SHA_MISMATCH")

def ghcr_upload(repo, filename, expected, size):
    token=ghcr_auth(repo)
    url=f"https://ghcr.io/v2/{repo}/blobs/{expected}"
    status,_,_=api("HEAD",url,token)
    if status==200: return
    if status!=404: die("GHCR_BLOB_HEAD_HTTP_"+str(status))
    status,headers,_=api("POST",f"https://ghcr.io/v2/{repo}/blobs/uploads/",token,data=b"")
    if status!=202: die("GHCR_UPLOAD_INIT_HTTP_"+str(status))
    location=urllib.parse.urljoin("https://ghcr.io",headers.get("Location",headers.get("location","")))
    if not headers.get("Location",headers.get("location","")): die("GHCR_UPLOAD_LOCATION_MISSING")
    if urllib.parse.urlsplit(location).hostname!="ghcr.io": die("GHCR_UPLOAD_UNTRUSTED_REDIRECT")
    with tempfile.NamedTemporaryFile(mode="w+",delete=True) as hdr:
        proc=subprocess.run([
            "curl","--silent","--show-error","--fail","--retry","2",
            "--max-time","1800","--request","PATCH",
            "--header","Authorization: Bearer "+token,
            "--header","Content-Type: application/octet-stream",
            "--upload-file",str(filename),
            "--dump-header",hdr.name,"--output","/dev/null",location,
        ],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        if proc.returncode: die("GHCR_UPLOAD_PATCH_FAILED_"+str(proc.returncode))
        headers_text=Path(hdr.name).read_text()
    matches=re.findall(r"(?im)^location:\s*(\S+)\s*$",headers_text)
    if not matches: die("GHCR_PATCH_LOCATION_MISSING")
    location=urllib.parse.urljoin("https://ghcr.io",matches[-1])
    parts=urllib.parse.urlsplit(location)
    if parts.hostname!="ghcr.io": die("GHCR_PATCH_REDIRECT_UNTRUSTED")
    query=[(k,v) for k,v in urllib.parse.parse_qsl(parts.query) if k!="digest"]+[("digest",expected)]
    finish=urllib.parse.urlunsplit((parts.scheme,parts.netloc,parts.path,urllib.parse.urlencode(query),""))
    status,_,_=api("PUT",finish,token,data=b"")
    if status not in (200,201,202): die("GHCR_UPLOAD_FINISH_HTTP_"+str(status))
    status,_,_=api("HEAD",url,token)
    if status!=200: die("GHCR_UPLOADED_BLOB_MISSING")

class HashWriter:
    def __init__(self,target):
        self.target=target
        self.hash=hashlib.sha256()
        self.size=0
    def write(self,data):
        self.hash.update(data)
        self.size+=len(data)
        return self.target.write(data)
    def flush(self):
        self.target.flush()
    def digest(self):
        return "sha256:"+self.hash.hexdigest()

def tar_layer(output, files):
    """files = (archive path, source Path OR bytes, mode)."""
    with open(output,"wb") as raw:
        compressed=HashWriter(raw)
        with gzip.GzipFile(fileobj=compressed,mode="wb",compresslevel=1,mtime=0) as gz:
            uncompressed=HashWriter(gz)
            with tarfile.open(fileobj=uncompressed,mode="w|",format=tarfile.PAX_FORMAT) as tar:
                for archive_name,source,mode in files:
                    info=tarfile.TarInfo(archive_name)
                    info.mode=mode
                    info.uid=info.gid=0
                    info.mtime=0
                    info.size=source.stat().st_size if isinstance(source,Path) else len(source)
                    with open(source,"rb") if isinstance(source,Path) else io.BytesIO(source) as inp:
                        tar.addfile(info,inp)
    desc={"mediaType":LAYER,"digest":compressed.digest(),"size":compressed.size}
    if desc["size"]>=LIMIT: die("NEW_LAYER_EXCEEDS_GHCR_LIMIT")
    return desc,uncompressed.digest()

def bootstrap(config,number,count):
    original=config.get("config",{})
    entry=original.get("Entrypoint") or []
    if isinstance(entry,str): entry=["/bin/sh","-c",entry]
    if not isinstance(entry,list) or any(not isinstance(e,str) for e in entry):
        die("SOURCE_ENTRYPOINT_UNSUPPORTED")
    if (original.get("User") or "root") not in ("root","0"):
        die("SOURCE_USER_NOT_ROOT")
    exec_cmd="exec "+" ".join(shlex.quote(x) for x in entry)+' "$@"' if entry else 'exec "$@"'
    part_pattern=f"/opt/recovery-chunks/layer{number:02d}/part-*"
    return (("#!/bin/bash\nset -euo pipefail\n"
        "# The original source OCI layer is reconstructed before the original Worker starts.\n"
        "if [ ! -f /tmp/oci-restored.ok ]; then\n"
        "  shopt -s nullglob\n"
        f"  parts=({part_pattern})\n"
        "  if [ \""+"$"+"{#parts[@]}"+f"\" -ne {count} ]; then echo MISSING_LAYER_PART >&2; exit 32; fi\n"
        "  cat \""+"$"+"{parts[@]}"+'" | tar -xz -C /\n'
        "  touch /tmp/oci-restored.ok\n"
        "fi\n"+exec_cmd+"\n")).encode()

def legal_files(root):
    if not Path("third_party_licenses").is_dir() or not Path("NOTICE-THIRD-PARTY.md").is_file():
        die("LEGAL_TEXTS_UNAVAILABLE")
    directory=root/"license-files"
    directory.mkdir()
    shutil.copytree("third_party_licenses",directory/"third_party_licenses")
    shutil.copy("NOTICE-THIRD-PARTY.md",directory/"NOTICE-THIRD-PARTY.md")
    proc=subprocess.run([sys.executable,"scripts/collect_official_policies.py","--out",str(directory/"official-policies")],
        stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=180)
    if proc.returncode: die("OFFICIAL_LEGAL_DOCUMENT_FETCH_FAILED")
    return directory

def main():
    source=os.environ.get("OCI_SOURCE_IMAGE","")
    target=os.environ.get("GHCR_DEST_IMAGE","")
    if not source or not re.fullmatch(r"ghcr.io/[a-z0-9_.-]+/[a-z0-9_.-]+:[A-Za-z0-9_.-]+",target):
        die("SOURCE_SECRET_OR_DEST_IMAGE_MISSING")
    dest_repo,tag=target.removeprefix("ghcr.io/").rsplit(":",1)
    source_repo,source_tag,source_token=source_auth(source)
    manifest=source_manifest(source_repo,source_tag,source_token)
    layers=manifest["layers"]
    oversize=[i for i,x in enumerate(layers) if x["size"]>=LIMIT]
    if len(oversize)!=1: die("EXPECTED_EXACTLY_ONE_OVERSIZE_LAYER")
    giant=oversize[0]
    parts=(layers[giant]["size"]+CHUNK-1)//CHUNK
    if parts<2 or parts>20: die("CHUNK_COUNT_OUT_OF_RANGE")
    with source_stream(source_repo,manifest["config"]["digest"],source_token) as res:
        raw_config=res.read(2_500_001)
    if len(raw_config)>2_500_000 or digest(raw_config)!=manifest["config"]["digest"]:
        die("SOURCE_CONFIG_DIGEST_INVALID")
    original=json.loads(raw_config)
    if original.get("os")!="linux" or original.get("architecture")!="amd64" or len(original["rootfs"]["diff_ids"])!=len(layers):
        die("SOURCE_CONFIG_ARCH_OR_DIFF_IDS_INVALID")
    start_script=bootstrap(original,giant+1,parts)
    print(f"SOURCE_VALIDATED layers={len(layers)} large_layer={giant+1} parts={parts}",flush=True)
    with tempfile.TemporaryDirectory(prefix="oci-split-") as folder:
        tmp=Path(folder)
        licenses=legal_files(tmp)
        new_layers=[]
        diffids=[]
        for n,desc in enumerate(layers):
            if n!=giant:
                if desc["size"]>=LIMIT: die("UNEXPECTED_OTHER_HUGE_LAYER")
                filename=tmp/"original-layer.blob"
                download_verified(source_repo,desc,source_token,filename)
                ghcr_upload(dest_repo,filename,desc["digest"],desc["size"])
                filename.unlink()
                new_layers.append({k:desc[k] for k in ("mediaType","digest","size")})
                diffids.append(original["rootfs"]["diff_ids"][n])
                print(f"ORIGINAL_LAYER_{n+1:02d}_UNCHANGED",flush=True)
            else:
                original_hash=hashlib.sha256()
                consumed=0
                with source_stream(source_repo,desc["digest"],source_token) as inp:
                    for p in range(parts):
                        desired=min(CHUNK,desc["size"]-consumed)
                        chunkfile=tmp/"compressed-source-chunk.bin"
                        with open(chunkfile,"wb") as out:
                            remaining=desired
                            while remaining:
                                part=inp.read(min(remaining,BLOCK))
                                if not part: die("GIANT_LAYER_TRUNCATED")
                                consumed+=len(part)
                                remaining-=len(part)
                                original_hash.update(part)
                                out.write(part)
                        package=tmp/"carrier-layer.tar.gz"
                        newdesc,newdiff=tar_layer(package,[(f"opt/recovery-chunks/layer{n+1:02d}/part-{p:05d}.oci",chunkfile,0o444)])
                        chunkfile.unlink()
                        ghcr_upload(dest_repo,package,newdesc["digest"],newdesc["size"])
                        package.unlink()
                        new_layers.append(newdesc)
                        diffids.append(newdiff)
                        print(f"LARGE_LAYER_PART_{p+1:02d}_OF_{parts}_UPLOADED",flush=True)
                    if inp.read(1): die("GIANT_LAYER_EXTRA_BYTES")
                if consumed!=desc["size"] or "sha256:"+original_hash.hexdigest()!=desc["digest"]:
                    die("GIANT_SOURCE_DIGEST_MISMATCH")
                print("ORIGINAL_GIANT_BLOB_SHA256_MATCH",flush=True)
        files=[]
        for path in sorted(licenses.rglob("*")):
            if path.is_file():
                if path.is_symlink(): die("LEGAL_FILE_SYMLINK")
                files.append(("opt/recovery-licenses/"+path.relative_to(licenses).as_posix(),path,0o444))
        files.append(("opt/recovery/runtime-start.sh",start_script,0o755))
        overlay=tmp/"legal-overlay.tar.gz"
        ov_desc,ov_diff=tar_layer(overlay,files)
        ghcr_upload(dest_repo,overlay,ov_desc["digest"],ov_desc["size"])
        new_layers.append(ov_desc)
        diffids.append(ov_diff)
        overlay.unlink()
        config=copy.deepcopy(original)
        config["rootfs"]["diff_ids"]=diffids
        config["config"]["Entrypoint"]=["/bin/bash","/opt/recovery/runtime-start.sh"]
        config["config"].setdefault("Labels",{})["org.opencontainers.image.title"]="LTX 2.3 10Eros RunPod"
        config["author"]=""
        updated_history=[]
        source_layers=0
        for old in config.get("history",[]):
            if old.get("empty_layer"):
                updated_history.append(old)
                continue
            if source_layers==giant:
                updated_history.extend({"created_by":f"Preserved source OCI as {i+1}/{parts} container-safe chunks"} for i in range(parts))
            else:
                if "I2V-Lab" in str(old) or "i2vltx" in str(old):
                    old={"created_by":"OCI source metadata normalized; original files unchanged"}
                updated_history.append(old)
            source_layers+=1
        if source_layers!=len(layers): die("SOURCE_HISTORY_COUNT_UNEXPECTED")
        updated_history.append({"created_by":"License notices and original-layer restoration bootstrap"})
        config["history"]=updated_history
        config_json=json.dumps(config,sort_keys=True,separators=(",",":")).encode()
        config_file=tmp/"config.json"
        config_file.write_bytes(config_json)
        ghcr_upload(dest_repo,config_file,digest(config_json),len(config_json))
        result={"schemaVersion":2,"mediaType":MANIFEST,
            "config":{"mediaType":CONFIG,"digest":digest(config_json),"size":len(config_json)},
            "layers":new_layers}
        manifest_json=json.dumps(result,sort_keys=True,separators=(",",":")).encode()
        token=ghcr_auth(dest_repo)
        url=f"https://ghcr.io/v2/{dest_repo}/manifests/{tag}"
        status,_,_=api("PUT",url,token,data=manifest_json,extra={"Content-Type":MANIFEST})
        if status not in (200,201,202): die("GHCR_MANIFEST_PUBLISH_HTTP_"+str(status))
        token=ghcr_auth(dest_repo)
        code,_,readback=api("GET",url,token,accept=MANIFEST)
        if code!=200 or digest(readback)!=digest(manifest_json): die("GHCR_READBACK_FAILED")
        result_digest=digest(manifest_json)
        print("GHCR_IMAGE_PUBLISHED",result_digest,flush=True)
        summary=os.getenv("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary,"a") as out:
                out.write(f"## GHCR OCI Published\n\n- Image: {target}\n- Digest: {result_digest}\n")
                out.write("- Original Worker/Workflow/model bytes preserved. Large OCI layer restored at worker startup.\n")
                out.write("- RunPod container disk: 120GB recommended. GPU video not tested.\n")

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        # Do not print registry URLs or credentials to public GitHub Actions logs.
        print("OCI_PUBLISH_FAILED",type(e).__name__,str(e).split("?")[0][:120],file=sys.stderr)
        raise SystemExit(2)
