#!/usr/bin/env python3
"""Refresh only the existing GHCR image license/NOTICE overlay, never model blobs.

Source: fixed, previously GPU-validated GHCR image, not the original registry.
All 22 original model/runtime transport layers are reused by immutable digest.
No original account reference, GPU, large image pull, or Docker daemon required.
"""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import sys
import tarfile
import tempfile
import urllib.parse

SOURCE_DIGEST="sha256:434141dc283fe49808b93139de7905a9fb190071fbbe811809b1f021d9f1ceb5"
REPO="open-video-recovery/ltx23-10eros-licensed"
TAG="ltx23-v14"
EXTRA_TAG="ltx23-v14-5ch"
BASE=f"https://ghcr.io/v2/{REPO}"

spec=importlib.util.spec_from_file_location("oci_helpers","scripts/oci/repack_public_oci.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def required(ok, code):
    if not ok:
        raise RuntimeError(code)

def get_json_blob(desc,token):
    required(desc["size"]<=5_000_000,"BLOB_TOO_LARGE")
    code,_,raw=mod.api("GET",BASE+"/blobs/"+desc["digest"],token,limit=5_000_000)
    required(code==200 and len(raw)==desc["size"] and mod.digest(raw)==desc["digest"],
             "OCI_BLOB_SHA256_CHECK_FAILED")
    return raw

def main():
    token=mod.ghcr_auth(REPO)
    code,_,raw=mod.api("GET",BASE+"/manifests/"+SOURCE_DIGEST,token,accept=mod.MANIFEST)
    required(code==200 and mod.digest(raw)==SOURCE_DIGEST,"ORIGINAL_GHCR_MANIFEST_MISSING")
    manifest=json.loads(raw)
    required(len(manifest.get("layers",[]))==23,"UNEXPECTED_SOURCE_LAYOUT")
    cfg=json.loads(get_json_blob(manifest["config"],token))
    required(len(cfg.get("rootfs",{}).get("diff_ids",[]))==23,"DIFF_ID_COUNT_INVALID")
    original_layers=manifest["layers"][:-1]
    original_digests=[x["digest"] for x in original_layers]
    last=manifest["layers"][-1]
    with tarfile.open(fileobj=io.BytesIO(get_json_blob(last,token)),mode="r:gz") as tf:
        old={}
        for item in tf:
            if not item.isfile():continue
            required(item.size<=4_000_000,"LEGAL_FILE_TOO_LARGE")
            required(item.name.startswith("opt/recovery-licenses/")
                     or item.name=="opt/recovery/runtime-start.sh",
                     "UNEXPECTED_LEGAL_OVERLAY_ENTRY")
            obj=tf.extractfile(item)
            required(obj is not None,"LEGAL_ENTRY_MISSING")
            old[item.name]=(obj.read(),item.mode)
    notice_name="opt/recovery-licenses/NOTICE-THIRD-PARTY.md"
    required(notice_name in old,"NOTICE_NOT_IN_SOURCE")
    notice=Path("NOTICE-THIRD-PARTY.md").read_bytes()
    required(len(notice)>1500 and b"LTX-2 Community" in notice and b"Gemma" in notice,
             "NEW_NOTICE_MISSING_UPSTREAM_CREDIT")
    old[notice_name]=(notice,0o444)

    # Guarantee that we preserve the archived legal policies and Worker bootstrap.
    required("opt/recovery/runtime-start.sh" in old,"BOOTSTRAP_NOT_PRESERVED")
    required(sum(k.startswith("opt/recovery-licenses/") for k in old)>=9,
             "LICENSE_BUNDLE_INCOMPLETE")
    required(any(k.endswith("/Gemma-NOTICE.txt") for k in old),
             "GEMMA_NOTICE_NOT_INCLUDED")
    required(any(k.endswith("/LTX-Acceptable-Use-Policy.pdf") for k in old),
             "LTX_AUP_NOT_INCLUDED")

    with tempfile.TemporaryDirectory(prefix="notice-refresh-") as folder:
        tmp=Path(folder)
        overlay=tmp/"overlay.tar.gz"
        files=[(name,data,mode) for name,(data,mode) in sorted(old.items())]
        layer,new_diffid=mod.tar_layer(overlay,files)
        required(layer["size"]<3_000_000,"NEW_OVERLAY_TOO_LARGE")

        out=copy.deepcopy(manifest)
        out["layers"][-1]=layer
        updated=copy.deepcopy(cfg)
        updated["rootfs"]["diff_ids"][-1]=new_diffid
        # OCI config labels are optional descriptive metadata. Do not retain
        # unrelated original builder/origin labels in the public release.
        updated["config"]["Labels"]={
            "org.opencontainers.image.title":"LTX 2.3 10Eros v1.4 RunPod",
            "org.opencontainers.image.description":"Model, original workflow, packaged upstream legal notices",
            "org.opencontainers.image.licenses":"LTX-2 Community; Gemma Terms; GPL-3.0; additional upstream terms",
        }
        updated["author"]=""
        # Neutralize home-directory build metadata without changing on-disk
        # packages, model weights, Worker, commands, or other OCI layers.
        for history in updated.get("history",[]):
            for field in ("created_by","comment"):
                value=history.get(field)
                if isinstance(value,str):
                    value=re.sub(r"/home/[^/ \t\r\n'\"$]+","/home/USER",value)
                    value=re.sub(r"(?i)[A-Z]:[/\\]Users[/\\][^/\\ \t\r\n'\"]+",
                                 "C:/Users/USER",value)
                    history[field]=value
        if updated.get("history"):
            updated["history"][-1]["created_by"]="Updated upstream licenses and NOTICE for distribution"
        raw_config=json.dumps(updated,sort_keys=True,separators=(",",":")).encode()
        cfgfile=tmp/"config.json"
        cfgfile.write_bytes(raw_config)
        out["config"]={"mediaType":mod.CONFIG,
                       "digest":mod.digest(raw_config),"size":len(raw_config)}
        raw_manifest=json.dumps(out,sort_keys=True,separators=(",",":")).encode()
        manifest_digest=mod.digest(raw_manifest)
        required([x["digest"] for x in out["layers"][:-1]]==original_digests,
                 "ORIGINAL_MODEL_LAYER_CHANGED")

        mod.ghcr_upload(REPO,overlay,layer["digest"],layer["size"])
        mod.ghcr_upload(REPO,cfgfile,out["config"]["digest"],len(raw_config))
        for tag in (TAG,EXTRA_TAG):
            bearer=mod.ghcr_auth(REPO)
            location=BASE+"/manifests/"+tag
            status,_,_=mod.api("PUT",location,bearer,data=raw_manifest,
                               extra={"Content-Type":mod.MANIFEST})
            required(status in (200,201,202),"GHCR_MANIFEST_PUSH_FAILED_"+str(status))
            bearer=mod.ghcr_auth(REPO)
            status,_,readback=mod.api("GET",location,bearer,accept=mod.MANIFEST)
            required(status==200 and mod.digest(readback)==manifest_digest,
                     "GHCR_MANIFEST_READBACK_FAILED")
            print("GHCR_TAG_VERIFIED",tag,flush=True)
        # This tag must be anonymously readable for a 5ch link.
        url="https://ghcr.io/token?"+urllib.parse.urlencode({
            "service":"ghcr.io","scope":"repository:"+REPO+":pull"})
        code,_,body=mod.api("GET",url)
        required(code==200,"ANONYMOUS_TOKEN_UNAVAILABLE")
        anon=json.loads(body).get("token")
        required(anon,"ANONYMOUS_TOKEN_MISSING")
        code,_,readback=mod.api("GET",BASE+"/manifests/"+manifest_digest,anon,
                                accept=mod.MANIFEST)
        required(code==200 and mod.digest(readback)==manifest_digest,
                 "ANONYMOUS_MANIFEST_GET_FAILED")
        print("ANONYMOUS_GHCR_PULL_CONFIRMED",flush=True)
        print("REUSED_UNCHANGED_MODEL_RUNTIME_LAYERS",len(original_layers),flush=True)
        print("LICENSE_FILES_PRESERVED",sum(k.startswith("opt/recovery-licenses/") for k in old),flush=True)
        print("PUBLIC_RELEASE_DIGEST",manifest_digest,flush=True)
        summary=os.environ.get("GITHUB_STEP_SUMMARY")
        if summary:
            with open(summary,"a") as f:
                f.write("## LTX 2.3 / 10Eros final GHCR release\n\n")
                f.write("- Fixed OCI: ghcr.io/"+REPO+"@"+manifest_digest+"\n")
                f.write("- Reused all 22 existing model/runtime layers, unchanged\n")
                f.write("- Refreshed LICENSE/NOTICE final layer and normalized descriptive OCI metadata\n")
                f.write("- Anonymous manifest pull: verified\n")
                f.write("- Reference GPU smoke: prior immutable OCI generated MP4 on 24GB; ")
                f.write("new license/metadata-only repack not GPU-retested\n")

if __name__=="__main__":
    try:
        main()
    except Exception as e:
        # Avoid printing raw metadata, registry tokens or private references.
        print("RELEASE_FAILED",type(e).__name__,str(e)[:100],file=sys.stderr)
        sys.exit(2)
