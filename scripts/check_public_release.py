#!/usr/bin/env python3
"""Compliance preflight for an image containing real LTX/Gemma model weights.

NOT a legal determination. The public model build must explicitly call
    python scripts/check_public_release.py --mode full-public
before any real-weight GHCR push.

The dummy OCI contract test uses --mode fixture only.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "legal/public-ghcr-release-gates.json"
FILES = {
    "ltx": ROOT / "third_party_licenses/LTX-2-Community-License-2026-01-05.txt",
    "gemma": ROOT / "third_party_licenses/Gemma-Terms-of-Use-2026-04-01.md",
    "gemma_notice": ROOT / "third_party_licenses/Gemma-NOTICE.txt",
    "comfy": ROOT / "third_party_licenses/ComfyUI-GPL-3.0.txt",
}
REQUIRED_GATE_NAMES = {
    "ltx_aup_copy",
    "gemma_prohibited_policy_copy",
    "comfyui_node_notices_source_access",
    "binding_downstream_acceptance_mechanism",
    "restricted_recipient_export_compliance",
    "model_license_review_and_signoff",
    "original_workflow_rights_or_independent_workflow",
    "full_model_oci_build_and_digest",
    "runpod_gpu_mp4_reproduction",
}


def materials_check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    files = {name: root / path.relative_to(ROOT) for name, path in FILES.items()}
    for name, path in files.items():
        if not path.is_file() or path.stat().st_size < 40:
            errors.append("MISSING_OR_TOO_SMALL:" + name)
    if not errors:
        ltx = files["ltx"].read_text(encoding="utf-8")
        gemma = files["gemma"].read_text(encoding="utf-8")
        notice = files["gemma_notice"].read_text(encoding="utf-8").strip()
        comfy = files["comfy"].read_text(encoding="utf-8")
        if not all(x in ltx for x in ("January 5, 2026", "Attachment A", "Distribution and Redistribution")):
            errors.append("LTX_LICENSE_INCOMPLETE")
        if not all(x in gemma for x in ("April 1, 2026", "Section 3", "Gemma Terms of Use")):
            errors.append("GEMMA_TERMS_INCOMPLETE")
        required_notice = "Gemma is provided under and subject to the Gemma Terms of Use found at ai.google.dev/gemma/terms"
        if notice != required_notice:
            errors.append("GEMMA_REQUIRED_NOTICE_MISMATCH")
        if "GNU GENERAL PUBLIC LICENSE" not in comfy or "Version 3" not in comfy:
            errors.append("COMFYUI_LICENSE_INCOMPLETE")
    return errors


def release_check(root: Path = ROOT, *, mode: str = "fixture") -> list[str]:
    errors = materials_check(root)
    if mode == "fixture":
        return errors
    if mode != "full-public":
        return errors + ["UNKNOWN_RELEASE_MODE"]
    register_path = root / "legal/public-ghcr-release-gates.json"
    try:
        record = json.loads(register_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return errors + ["PUBLIC_RELEASE_REGISTER_INVALID"]
    if record.get("decision") != "APPROVED":
        errors.append("PUBLIC_MODEL_RELEASE_BLOCKED")
    gates = record.get("gates", {})
    for name in sorted(REQUIRED_GATE_NAMES):
        gate = gates.get(name, {})
        if gate.get("status") != "verified" or not gate.get("evidence"):
            errors.append("UNVERIFIED_RELEASE_GATE:" + name)
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("fixture", "full-public"), default="fixture")
    args = parser.parse_args()
    failures = release_check(mode=args.mode)
    for value in failures:
        print("FAIL:", value, file=sys.stderr)
    if failures:
        raise SystemExit(2)
    print("SOURCE_MATERIALS_PRESENT" if args.mode == "fixture" else "PUBLIC_RELEASE_GATE_APPROVED")


if __name__ == "__main__":
    main()
