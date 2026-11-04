#!/usr/bin/env python3
"""Split an already acquired model into OCI-friendly chunks; restore offline.

Designed for remote builders: GHCR has a 10 GB compressed-layer cap and
upload-time restrictions. A model larger than that must NOT become one layer.
No network calls, GPU, or dependencies. Never uses a Docker Hub image.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

BLOCK = 4 * 1024 * 1024
DEFAULT_CHUNK = 6 * 1024 ** 3
MAX_CHUNK = 8 * 1024 ** 3


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(BLOCK), b""):
            value.update(chunk)
    return value.hexdigest()


def validate_basename(value: str) -> str:
    if not isinstance(value, str) or not value or Path(value).name != value:
        raise ValueError("INVALID_PART_FILENAME")
    if value.startswith(".") or "/" in value or "\\" in value:
        raise ValueError("UNSAFE_PART_FILENAME")
    return value


def split(source: Path, directory: Path, *, chunk_bytes: int = DEFAULT_CHUNK, expected_sha: str = "") -> Path:
    if not source.is_file() or source.is_symlink():
        raise ValueError("INPUT_MODEL_NOT_REGULAR_FILE")
    if not 1 <= chunk_bytes <= MAX_CHUNK:
        raise ValueError("CHUNK_LIMIT_OUT_OF_RANGE")
    directory.mkdir(parents=True, exist_ok=True)
    if list(directory.iterdir()):
        raise ValueError("OUTPUT_DIRECTORY_MUST_BE_EMPTY")
    part_entries = []
    combined = hashlib.sha256()
    total = 0
    with source.open("rb") as reader:
        index = 0
        while True:
            name = f"part-{index:04d}.bin"
            target = directory / name
            part_digest = hashlib.sha256()
            part_size = 0
            with target.open("xb") as writer:
                while part_size < chunk_bytes:
                    data = reader.read(min(BLOCK, chunk_bytes - part_size))
                    if not data:
                        break
                    writer.write(data)
                    part_digest.update(data)
                    combined.update(data)
                    total += len(data)
                    part_size += len(data)
            if not part_size:
                target.unlink()
                break
            part_entries.append({"name": name, "bytes": part_size, "sha256": part_digest.hexdigest()})
            index += 1
    if not part_entries:
        raise ValueError("EMPTY_MODEL_FILE")
    value = combined.hexdigest()
    if expected_sha and value != expected_sha.lower():
        raise ValueError("MODEL_SHA256_MISMATCH")
    manifest = {
        "schema": "embedded-model-chunks-v1",
        "original_filename": source.name,
        "bytes": total,
        "sha256": value,
        "parts": part_entries,
    }
    manifest_path = directory / "chunks.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def assemble(manifest_path: Path, output: Path, *, remove_parts: bool = False) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema") != "embedded-model-chunks-v1":
        raise ValueError("CHUNK_MANIFEST_SCHEMA_INVALID")
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        raise ValueError("CHUNK_MANIFEST_EMPTY")
    base = manifest_path.parent
    if output.is_symlink():
        raise ValueError("OUTPUT_PATH_SYMLINK_FORBIDDEN")
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        if output.stat().st_size != manifest["bytes"] or digest(output) != manifest["sha256"]:
            raise ValueError("EXISTING_OUTPUT_INVALID")
        return {"status": "ALREADY_VERIFIED", "sha256": manifest["sha256"]}
    aggregate = hashlib.sha256()
    byte_count = 0
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(dir=output.parent, prefix=".stitch-", delete=False) as writer:
            temp_path = Path(writer.name)
            for index, entry in enumerate(parts):
                name = validate_basename(entry["name"])
                if name != f"part-{index:04d}.bin":
                    raise ValueError("CHUNK_ORDER_INVALID")
                part = base / name
                if part.is_symlink() or not part.is_file() or part.stat().st_size != entry["bytes"]:
                    raise ValueError("CHUNK_MISSING_OR_SIZE_MISMATCH:" + name)
                value = hashlib.sha256()
                with part.open("rb") as reader:
                    for block in iter(lambda: reader.read(BLOCK), b""):
                        writer.write(block)
                        value.update(block)
                        aggregate.update(block)
                        byte_count += len(block)
                if value.hexdigest() != entry["sha256"]:
                    raise ValueError("CHUNK_SHA256_MISMATCH:" + name)
            writer.flush()
            os.fsync(writer.fileno())
        if byte_count != manifest["bytes"] or aggregate.hexdigest() != manifest["sha256"]:
            raise ValueError("ASSEMBLED_MODEL_SHA256_MISMATCH")
        os.replace(temp_path, output)
        temp_path = None
        if remove_parts:
            for entry in parts:
                (base / validate_basename(entry["name"])).unlink()
        return {"status": "VERIFIED", "bytes": byte_count, "sha256": manifest["sha256"]}
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="command", required=True)
    one = modes.add_parser("split")
    one.add_argument("--input", required=True, type=Path)
    one.add_argument("--output-dir", required=True, type=Path)
    one.add_argument("--chunk-bytes", type=int, default=DEFAULT_CHUNK)
    one.add_argument("--require-sha", default="")
    two = modes.add_parser("assemble")
    two.add_argument("--manifest", required=True, type=Path)
    two.add_argument("--output", required=True, type=Path)
    two.add_argument("--remove-parts", action="store_true")
    args = parser.parse_args()
    if args.command == "split":
        print(split(args.input, args.output_dir, chunk_bytes=args.chunk_bytes, expected_sha=args.require_sha))
    else:
        print(json.dumps(assemble(args.manifest, args.output, remove_parts=args.remove_parts)))


if __name__ == "__main__":
    main()
