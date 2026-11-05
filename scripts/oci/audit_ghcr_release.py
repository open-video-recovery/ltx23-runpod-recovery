#!/usr/bin/env python3
"""Read-only pre-Public audit of the EXACT GHCR image, never a Docker Hub proxy.

Prints finding categories and ordinal positions, not raw labels, URLs,
usernames, secrets, file content or entire image config. Does not alter GHCR.
"""
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tarfile
import importlib.util

PIN="sha256:434141dc283fe49808b93139de7905a9fb190071fbbe811809b1f021d9f1ceb5"
REPO="open-video-recovery/ltx23-10eros-licensed"
BASE=f"https://ghcr.io/v2/{REPO}"
spec=importlib.util.spec_from_file_location("oci_publisher","scripts/oci/repack_public_oci.py")
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def check(cond, reason):
    if not cond:
        raise RuntimeError(reason)

def get_blob(token,desc,max_bytes=5_000_000):
    check(desc.get("size",10**12) <= max_bytes,"BLOB_LARGER_THAN_AUDIT_BUDGET")
    code,_,raw=mod.api("GET",BASE+"/blobs/"+desc["digest"],token,limit=max_bytes)
    check(code==200,"BLOB_UNREADABLE_HTTP_"+str(code))
    check(len(raw)==desc["size"],"BLOB_SIZE_MISMATCH")
    check(mod.digest(raw)==desc["digest"],"BLOB_SHA256_MISMATCH")
    return raw

def flags(value,source_owner):
    s=str(value)
    l=s.lower()
    signals=[]
    if source_owner and source_owner in l: signals.append("SOURCE_DOCKERHUB_OWNER")
    if "i2v-lab" in l or "i2v_lab" in l: signals.append("LEGACY_PROJECT_NAME")
    if re.search(r"(?i)(?:[A-Za-z]:[\\/]+Users[\\/]|/home/[^/ \t\r\n'\"$]+)",s):
        signals.append("USER_HOME_PATH")
    if re.search(r"\b[A-Za-z0-9_.+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",s):
        signals.append("EMAIL_ADDRESS")
    if re.search(r"(?i)(?:password|passwd|api[_-]?key|secret|token)\s*[:=]\s*['\"]?[\w./+=-]{8,}",s):
        signals.append("POSSIBLE_SECRET_LITERAL")
    if re.search(r"(?i)https?://(?:www\.)?github\.com/[a-z0-9_.-]+/[a-z0-9_.-]+",s):
        signals.append("GITHUB_REPOSITORY_URL")
    if re.search(r"(?i)(?:docker\.io|hub\.docker\.com)/[a-z0-9_.-]+/",s):
        signals.append("DOCKERHUB_URL")
    return sorted(set(signals))

def main():
    source=os.environ.get("OCI_SOURCE_IMAGE","").removeprefix("docker.io/")
    check("/" in source,"SOURCE_REFERENCE_SECRET_MISSING")
    source_owner=source.split("/",1)[0].lower()
    token=mod.ghcr_auth(REPO)
    code,_,raw=mod.api("GET",BASE+"/manifests/"+PIN,token,accept=mod.MANIFEST)
    check(code==200,"GHCR_PINNED_MANIFEST_HTTP_"+str(code))
    check(mod.digest(raw)==PIN,"PINNED_MANIFEST_DIGEST_NOT_EQUAL")
    image=json.loads(raw)
    check(image.get("schemaVersion")==2 and "config" in image and "layers" in image,"NOT_IMAGE_MANIFEST")
    config=json.loads(get_blob(token,image["config"]))
    check(config.get("architecture")=="amd64" and config.get("os")=="linux","IMAGE_PLATFORM_UNEXPECTED")
    entries=image["layers"]
    check(len(entries)>16,"OVERSIZED_LAYER_NOT_SPLIT")
    check(max(d["size"] for d in entries)<10_000_000_000,"GHCR_LAYER_OVER_LIMIT")
    check(config.get("rootfs",{}).get("type")=="layers","CONFIG_ROOTFS_INVALID")
    check(len(config["rootfs"].get("diff_ids",[]))==len(entries),"DIFFIDS_LAYER_COUNT_MISMATCH")
    print("PINNED_IMAGE_VERIFIED",PIN)
    print("OCI_LAYOUT layers="+str(len(entries))+" history="+str(len(config.get("history",[]))))

    findings=[]
    def audit(field, value, ordinal):
        categories=flags(value,source_owner)
        if categories:
            findings.append({"field":field,"ordinal":ordinal,"categories":categories})

    for key,val in (image.get("annotations") or {}).items(): audit("manifest_annotation",key+"="+str(val),0)
    for key,val in (config.get("config",{}).get("Labels") or {}).items():audit("label",key+"="+str(val),0)
    for index,env in enumerate(config.get("config",{}).get("Env") or []):audit("environment",env,index+1)
    for key in ("author","created"): audit("image_"+key,config.get(key) or "",0)
    for key in ("Entrypoint","Cmd","WorkingDir","User"):
        audit("config_"+key,config.get("config",{}).get(key),0)
    history=config.get("history",[])
    for index,record in enumerate(history):
        for field in ("author","comment","created_by"):
            if record.get(field): audit("history_"+field,record[field],index+1)
    print("METADATA_FLAGS",json.dumps(findings,ensure_ascii=False))
    # Source layers smaller than 500KB can be inspected without model downloads.
    scanned=0
    small_content_flags=[]
    for index,desc in enumerate(entries[:-1]):
        if desc["size"] > 500_000:continue
        raw_layer=get_blob(token,desc,max_bytes=510_000)
        try:
            with tarfile.open(fileobj=io.BytesIO(raw_layer),mode="r:*") as tar:
                for member in tar:
                    x=flags(member.name,source_owner)
                    if x: small_content_flags.append({"layer":index+1,"kind":"tar_entry","flags":x})
                    if member.isfile() and member.size < 300_000 and member.name.endswith((".py",".json",".yaml",".yml",".txt",".md",".sh",".ini",".cfg",".toml")):
                        stream=tar.extractfile(member)
                        if stream:
                            text=stream.read(300_001).decode("utf-8","replace")
                            x=flags(text,source_owner)
                            if x: small_content_flags.append({"layer":index+1,"kind":"small_text","flags":x})
            scanned+=1
        except tarfile.TarError:
            small_content_flags.append({"layer":index+1,"kind":"cannot_read_tar","flags":["UNINSPECTED"]})
    print("SMALL_LAYERS_INSPECTED",scanned)
    print("SMALL_LAYER_FLAGS",json.dumps(small_content_flags,ensure_ascii=False))

    legal_layer_desc=entries[-1]
    raw=get_blob(token,legal_layer_desc,max_bytes=8_000_000)
    names={}
    with tarfile.open(fileobj=io.BytesIO(raw),mode="r:gz") as tar:
        for member in tar:
            check(member.name.startswith("opt/recovery-licenses/") or member.name=="opt/recovery/runtime-start.sh","UNEXPECTED_LAST_LAYER_ENTRY")
            if member.isfile():
                check(member.size<=4_000_000,"LICENSE_FILE_TOO_LARGE")
                file=tar.extractfile(member)
                names[member.name]=file.read() if file else b""
    root="opt/recovery-licenses/"
    required={
        "third_party_licenses/LTX-2-Community-License-2026-01-05.txt":b"LTX-2 Community License Agreement",
        "third_party_licenses/Gemma-Terms-of-Use-2026-04-01.md":b"Gemma Terms of Use",
        "third_party_licenses/Gemma-NOTICE.txt":b"Gemma is provided under and subject",
        "third_party_licenses/ComfyUI-GPL-3.0.txt":b"GNU GENERAL PUBLIC LICENSE",
        "NOTICE-THIRD-PARTY.md":b"Third-party attribution",
        "official-policies/LTX-Acceptable-Use-Policy.pdf":b"%PDF-",
        "official-policies/Gemma-Terms-Official.html":b"Gemma",
        "official-policies/Gemma-Prohibited-Use-Policy-Official.html":b"Gemma",
        "official-policies/policy-snapshot.json":b"documents",
    }
    details=[]
    for short,marker in required.items():
        data=names.get(root+short)
        status=("present" if data is not None else "MISSING")
        marker_ok=bool(data and (data.startswith(marker) if short.endswith(".pdf") else marker.lower() in data.lower()))
        details.append({"file":short,"status":status,"bytes":len(data) if data is not None else 0,"marker_ok":marker_ok})
    print("EMBEDDED_LICENSES",json.dumps(details,ensure_ascii=False))
    snapshot=names.get(root+"official-policies/policy-snapshot.json")
    snap_checks=[]
    if snapshot:
        doc=json.loads(snapshot)
        for x in doc.get("documents",[]):
            key=root+"official-policies/"+x["file"]
            value=names.get(key)
            snap_checks.append({"document":x["file"],"present":value is not None,"sha256_matches":bool(value is not None and hashlib.sha256(value).hexdigest()==x["sha256"])})
    print("POLICY_SHA_CHECKS",json.dumps(snap_checks,ensure_ascii=False))
    bootstrap=names.get("opt/recovery/runtime-start.sh",b"")
    print("BOOTSTRAP_PRESENT",bootstrap.startswith(b"#!/bin/bash"))
    print("UNSCANNED_LARGE_LAYER_COUNT",sum(1 for d in entries[:-1] if d["size"]>500_000))
    print("THIRD_PARTY_RUNTIME_CODE_LICENSE","NOT_VERIFIED")
    print("ENFORCEABLE_DOWNSTREAM_TERMS","NOT_VERIFIED")
    print("PUBLIC_REPO_GIT_HISTORY_PRIVACY","NOT_VERIFIED")
    errors=bool(findings or small_content_flags or not all(x["marker_ok"] for x in details) or not all(x["sha256_matches"] for x in snap_checks) or len(snap_checks)!=3 or not bootstrap)
    print("ACTUAL_GHCR_METADATA_AND_NOTICE_AUDIT", "FAIL" if errors else "PASS_WITH_LIMITATIONS")
    print("PUBLIC_RELEASE_AUTHORIZATION","BLOCKED_PENDING_RIGHTS_AND_HISTORY_REVIEW")
    summary=os.getenv("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a") as out:
            out.write("## Immutable GHCR release audit\n\n")
            out.write("**Pinned OCI metadata and final license layer:** "+("FAIL" if errors else "PASS with known limits")+"\n\n")
            out.write("- Labels/history flags: "+str(len(findings))+"\n")
            out.write("- Small tar flags: "+str(len(small_content_flags))+"\n")
            out.write("- Embedded license/policy files inspected: "+str(len(details))+"\n")
            out.write("- Full source-layer binary content: NOT scanned; downstream source-code rights: NOT cleared\n")
            out.write("- Git commit history exposure: NOT remediated\n")
            out.write("- **Public release: BLOCKED until legal & privacy review**\n")
    if errors:sys.exit(2)

if __name__=="__main__":
    try:main()
    except Exception as exc:
        # Avoid exposing secret source reference or any potentially identifying path.
        print("PRIVATE_GHCR_AUDIT_ERROR",type(exc).__name__,str(exc).split("?")[0][:90],file=sys.stderr)
        sys.exit(3)
