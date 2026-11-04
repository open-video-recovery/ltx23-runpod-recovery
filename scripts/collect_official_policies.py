#!/usr/bin/env python3
"""Collect official downstream policy documents for a *future* OCI build.

No model weights. Downloads only small public legal documents, recording
both official source URL and SHA-256. If a document is unavailable, fail
rather than omit it. Produced files must accompany real-weight images.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen

DOCUMENTS = [
    {
        "name": "LTX-Acceptable-Use-Policy.pdf",
        "source": "https://static.lightricks.com/legal/ltx-acceptable-use-policy.pdf",
        "marker": b"%PDF-",
        "content_type": "application/pdf",
    },
    {
        "name": "Gemma-Terms-Official.html",
        "source": "https://ai.google.dev/gemma/terms",
        "markers": [b"Gemma Terms of Use", b"Distribution and Redistribution"],
        "content_type": "text/html",
    },
    {
        "name": "Gemma-Prohibited-Use-Policy-Official.html",
        "source": "https://ai.google.dev/gemma/prohibited_use_policy",
        "markers": [b"Gemma Prohibited Use Policy", b"sexually explicit"],
        "content_type": "text/html",
    },
]
MAX_BYTES = 2 * 1024 * 1024


def verify_doc(doc: dict, contents: bytes):
    if not 500 <= len(contents) <= MAX_BYTES:
        raise ValueError("POLICY_DOCUMENT_SIZE_INVALID:" + doc["name"])
    if doc.get("marker") and not contents.startswith(doc["marker"]):
        raise ValueError("POLICY_DOCUMENT_FORMAT_INVALID:" + doc["name"])
    for marker in doc.get("markers", []):
        if marker not in contents:
            raise ValueError("POLICY_DOCUMENT_MISSING_REQUIRED_MARKER:" + doc["name"])


def collect(dest: Path):
    dest.mkdir(parents=True, exist_ok=True)
    evidence = []
    for doc in DOCUMENTS:
        request = Request(doc["source"], headers={"User-Agent": "LTX23-recovery-license-verifier/1.0"})
        with urlopen(request, timeout=90) as response:
            if response.status != 200:
                raise ValueError("POLICY_HTTP_ERROR:" + doc["name"])
            payload = response.read(MAX_BYTES + 1)
        verify_doc(doc, payload)
        output = dest / doc["name"]
        output.write_bytes(payload)
        evidence.append({
            "file": output.name,
            "source": doc["source"],
            "sha256": hashlib.sha256(payload).hexdigest(),
            "size_bytes": len(payload),
        })
        print("VERIFIED_LEGAL_DOCUMENT", output.name, evidence[-1]["sha256"], flush=True)
    manifest = {
        "retrieved_utc": datetime.now(timezone.utc).isoformat(),
        "documents": evidence,
        "note": "Downloaded evidence only; not legal redistribution authorization.",
    }
    (dest / "policy-snapshot.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    collect(parser.parse_args().out)
