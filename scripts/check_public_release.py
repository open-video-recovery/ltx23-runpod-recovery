#!/usr/bin/env python3
"""Check common model/OSS distribution packaging requirements.

Ensure applicable LTX, Gemma, and ComfyUI licenses/NOTICE are available
alongside the model distribution. This is NOT a legal approval, does not
create extra lawyer-signoff conditions, and does not supersede upstream terms.

--mode fixture checks source license materials.
--mode full-public additionally checks presence of distribution NOTICE/README.
"""
from __future__ import annotations
import argparse
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
# Historical audit registry is informational, not a blanket publication veto.
REQUIRED_NOTICE_FILES = ("NOTICE-THIRD-PARTY.md", "LICENSE", "README.md")


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
    # Standard release formatting: bundled license files, NOTICE and README.
    for item in REQUIRED_NOTICE_FILES:
        file = root / item
        if not file.is_file() or file.stat().st_size < 40:
            errors.append("MISSING_NOTICE_OR_README:" + item)
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
    print("SOURCE_MATERIALS_PRESENT" if args.mode == "fixture" else "STANDARD_LICENSE_NOTICE_MATERIALS_PRESENT")


if __name__ == "__main__":
    main()
