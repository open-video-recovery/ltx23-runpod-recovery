#!/usr/bin/env python3
"""Reassemble all OCI-bundled model chunks before starting ComfyUI.

This performs local file IO ONLY: no Hugging Face, Docker Hub, S3 or network.
The OCI has all required bytes already. Never claim the resulting workflow or
GPU was validated merely because the SHA-256 checks succeeded.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "scripts"))
from model_chunks import assemble, digest

SCHEMA = "full-model-embedded-oci-staging-v1"


def safe_path(s: str) -> Path:
    p = Path(s)
    if not s or p.is_absolute() or ".." in p.parts or "." in p.parts or "\\" in s:
        raise ValueError("UNSAFE_BUNDLE_PATH")
    return p


def restore(bundle_root: Path, model_root: Path) -> list[dict]:
    bundle_json = bundle_root / "bundle.json"
    if bundle_json.is_symlink():
        raise ValueError("UNSAFE_BUNDLE_SYMLINK")
    doc = json.loads(bundle_json.read_text(encoding="utf-8"))
    if doc.get("schema") != SCHEMA or not isinstance(doc.get("models"), list) or not doc["models"]:
        raise ValueError("INVALID_OCI_BUNDLE")
    outputs = []
    targets = set()
    for entry in doc["models"]:
        target = safe_path(entry["target"])
        manifest = safe_path(entry["manifest"])
        if target.suffix != ".safetensors" or target in targets:
            raise ValueError("INVALID_OR_DUPLICATE_MODEL_DESTINATION")
        targets.add(target)
        src = bundle_root / manifest
        if src.is_symlink() or not src.is_file():
            raise ValueError("MODEL_CHUNKS_MANIFEST_NOT_PRESENT")
        destination = model_root / target
        result = assemble(src, destination)
        if destination.stat().st_size != entry["bytes"] or result["sha256"] != entry["sha256"]:
            raise ValueError("LOCKED_MODEL_MISMATCH:" + entry.get("key", "?"))
        outputs.append({"key": entry["key"], **result})
        print("OFFLINE_MODEL_RESTORED", entry["key"], flush=True)
    return outputs


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bundle-root", type=Path, default=Path("/opt/recovery/model_bundle"))
    parser.add_argument("--model-root", type=Path, default=Path("/comfyui/models"))
    args = parser.parse_args()
    print(json.dumps(restore(args.bundle_root, args.model_root), indent=2))
