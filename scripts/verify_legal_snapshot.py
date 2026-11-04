#!/usr/bin/env python3
"""Verify bundled official policies against a build-time SHA256 manifest.

No network and no model weights. Reject missing, modified, extra or symlinked
files. This validates integrity, not the legality of public model publishing.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

EXPECTED_FILES = {
    "LTX-Acceptable-Use-Policy.pdf",
    "Gemma-Terms-Official.html",
    "Gemma-Prohibited-Use-Policy-Official.html",
}


def verify(root: Path) -> list[str]:
    issues = []
    try:
        doc = json.loads((root / "policy-snapshot.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ["LEGAL_SNAPSHOT_MANIFEST_UNREADABLE"]
    entries = doc.get("documents", [])
    if not isinstance(entries, list) or {x.get("file") for x in entries if isinstance(x, dict)} != EXPECTED_FILES:
        return ["LEGAL_SNAPSHOT_FILE_SET_INVALID"]
    for row in entries:
        filename = row["file"]
        path = root / filename
        if path.is_symlink() or not path.is_file():
            issues.append("LEGAL_SNAPSHOT_FILE_MISSING:" + filename)
            continue
        data = path.read_bytes()
        if len(data) != row.get("size_bytes"):
            issues.append("LEGAL_SNAPSHOT_SIZE_MISMATCH:" + filename)
        if hashlib.sha256(data).hexdigest() != row.get("sha256"):
            issues.append("LEGAL_SNAPSHOT_SHA256_MISMATCH:" + filename)
        if filename.endswith(".pdf") and not data.startswith(b"%PDF-"):
            issues.append("LEGAL_SNAPSHOT_PDF_INVALID")
        if filename.endswith(".html") and b"<html" not in data[:10000].lower():
            issues.append("LEGAL_SNAPSHOT_HTML_INVALID:" + filename)
    return issues


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, required=True)
    args = ap.parse_args()
    failures = verify(args.root)
    for failure in failures:
        print("FAIL:", failure, file=sys.stderr)
    if failures:
        raise SystemExit(2)
    print("OFFICIAL_LEGAL_SNAPSHOT_OFFLINE_SHA256_VERIFIED")
