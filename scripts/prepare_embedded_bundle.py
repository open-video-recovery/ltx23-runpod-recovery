#!/usr/bin/env python3
"""Create a cloud-builder OCI model-layer staging directory from validated files.

This program itself does NOT publish real model weights. No Docker Hub model
image is imported. All inputs must already have been obtained from the
original licensors / Hugging Face and verified against models.lock.json.

The resulting directory is intended as a Docker build context on a runner
with ample disk space (>= 250 GB practical allowance); do not use a normal
14 GB GitHub-hosted runner or commit model chunks to the source repository.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil
import sys

from model_chunks import DEFAULT_CHUNK, MAX_CHUNK, split
from verify_models import verify_one

SCHEMA = "full-model-embedded-oci-staging-v1"


def safe_relpath(value: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError("EMPTY_RELATIVE_PATH")
    candidate = Path(value)
    if candidate.is_absolute() or "." in candidate.parts or ".." in candidate.parts:
        raise ValueError("UNSAFE_RELATIVE_PATH")
    if any(not x or "\\" in x for x in candidate.parts):
        raise ValueError("UNSAFE_RELATIVE_PATH")
    return candidate


def prepare(lock_path: Path, model_root: Path, output_dir: Path, *,
            chunk_bytes: int = DEFAULT_CHUNK) -> dict:
    if not 1 <= chunk_bytes <= MAX_CHUNK:
        raise ValueError("INVALID_CHUNK_SIZE")
    if output_dir.exists() and any(output_dir.iterdir()):
        raise ValueError("OUTPUT_DIRECTORY_MUST_BE_EMPTY")
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    entries = lock.get("models")
    if not isinstance(entries, list) or not entries:
        raise ValueError("INVALID_MODELS_LOCK")
    keys = set()
    manifest_entries = []
    total = 0
    for entry in entries:
        key = entry.get("key")
        if not isinstance(key, str) or not key or any(c not in
                "abcdefghijklmnopqrstuvwxyz0123456789-" for c in key) or key in keys:
            raise ValueError("UNSAFE_OR_DUPLICATE_MODEL_KEY")
        keys.add(key)
        target = safe_relpath(entry.get("target"))
        if target.suffix != ".safetensors":
            raise ValueError("MODEL_TARGET_EXTENSION_INVALID")
        # Abort the entire operation before creating any chunks if a model
        # is absent, mismatched, or otherwise ineligible.
        print("VERIFYING_MODEL", key, flush=True)
        verify_one(entry, model_root)
        total += entry["size"]
    output_dir.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        key = entry["key"]
        target = safe_relpath(entry["target"])
        source = model_root / target
        parts_dir = output_dir / "model_chunks" / key
        record = split(source, parts_dir, chunk_bytes=chunk_bytes,
                       expected_sha=entry["sha256"])
        manifest_entries.append({
            "key": key,
            "target": str(target).replace("\\", "/"),
            "bytes": entry["size"],
            "sha256": entry["sha256"],
            "manifest": str(record.relative_to(output_dir)).replace("\\", "/"),
        })
    result = {
        "schema": SCHEMA,
        "source": "models.lock.json; each source SHA256 separately verified",
        "total_bytes": total,
        "models": manifest_entries,
    }
    (output_dir / "bundle.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("PREPARED_EMBEDDED_OCI_PARTS", len(entries), total, flush=True)
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--model-root", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--lock", type=Path, default=Path(__file__).resolve().parents[1] / "models.lock.json")
    ap.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK)
    args = ap.parse_args()
    prepare(args.lock, args.model_root, args.out, chunk_bytes=args.chunk_bytes)


if __name__ == "__main__":
    main()
