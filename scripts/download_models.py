#!/usr/bin/env python3
"""Fetch SHA-pinned public Hugging Face models without storing weights in Git."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import shutil
from verify_models import verify_one


def download_one(entry: dict, root: Path):
    from huggingface_hub import hf_hub_download
    destination = root / Path(entry["target"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        verify_one(entry, root)
        print("EXISTING_VERIFIED:", entry["key"], flush=True)
        return
    cached = Path(hf_hub_download(
        repo_id=entry["repo"], revision=entry["revision"],
        filename=entry["path"], token=os.getenv("HF_TOKEN") or None,
    ))
    if cached.stat().st_size != entry["size"]:
        raise ValueError("SOURCE_SIZE_MISMATCH:" + entry["key"])
    incoming = destination.with_name(destination.name + ".incoming")
    incoming.unlink(missing_ok=True)
    try:
        shutil.copyfile(cached, incoming)
        incoming.replace(destination)
        verify_one(entry, root)
    except Exception:
        destination.unlink(missing_ok=True)
        incoming.unlink(missing_ok=True)
        raise
    print("DOWNLOADED_VERIFIED:", entry["key"], flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-root", type=Path, required=True)
    parser.add_argument("--only", default="all")
    args = parser.parse_args()
    entries = json.loads((Path(__file__).resolve().parents[1] / "models.lock.json").read_text())["models"]
    keys = {"all", *(item["key"] for item in entries)}
    if args.only not in keys:
        parser.error("--only must be 'all' or one of: " + ", ".join(sorted(keys - {"all"})))
    for entry in entries:
        if args.only in ("all", entry["key"]):
            download_one(entry, args.model_root)


if __name__ == "__main__":
    main()
