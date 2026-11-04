#!/usr/bin/env python3
"""Verify model byte sizes and SHA-256 without network or GPU."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys


def stream_sha256(path: Path) -> str:
    checksum = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            checksum.update(block)
    return checksum.hexdigest()


def verify_one(entry: dict, model_root: Path) -> dict:
    target = Path(entry["target"])
    if target.is_absolute() or ".." in target.parts or target.suffix != ".safetensors":
        raise ValueError("UNSAFE_MODEL_TARGET")
    file = model_root / target
    if file.is_symlink() or not file.is_file():
        raise FileNotFoundError(str(file))
    size = file.stat().st_size
    if size != entry["size"]:
        raise ValueError(f"SIZE_MISMATCH:{entry['key']}:{size}")
    digest = stream_sha256(file)
    if digest != entry["sha256"]:
        raise ValueError(f"SHA256_MISMATCH:{entry['key']}:{digest}")
    return {"key": entry["key"], "status": "PASS", "bytes": size, "sha256": digest}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--lock", type=Path, default=Path(__file__).resolve().parents[1] / "models.lock.json")
    args = parser.parse_args()
    entries = json.loads(args.lock.read_text(encoding="utf-8"))["models"]
    errors = 0
    for entry in entries:
        try:
            print(json.dumps(verify_one(entry, args.model_root)), flush=True)
        except (OSError, ValueError) as error:
            errors += 1
            print(json.dumps({"key": entry["key"], "status": "FAIL", "error": str(error)}), file=sys.stderr)
    raise SystemExit(1 if errors else 0)


if __name__ == "__main__":
    main()
