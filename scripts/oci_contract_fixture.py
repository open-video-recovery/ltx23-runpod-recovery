#!/usr/bin/env python3
"""Generate a tiny fake checkpoint split across separate OCI layers.

This is not a model. It validates the image-bundled, offline reconstruction
contract without downloading, uploading or redistributing model weights.
"""
from __future__ import annotations
from pathlib import Path
import tempfile
from model_chunks import split, assemble

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "contract-fixture"

def make():
    if OUT.exists():
        raise RuntimeError("FIXTURE_OUTPUT_EXISTS")
    OUT.mkdir()
    try:
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "fake-weights.safetensors"
            source.write_bytes(b"FAKE TEST BYTES - NOT A MODEL\n" * 450)
            manifest = split(source, OUT, chunk_bytes=4096)
            assert len(list(OUT.glob("part-*.bin"))) == 4
            target = Path(tmp) / "restored.safetensors"
            assert assemble(manifest, target)["status"] == "VERIFIED"
            assert target.read_bytes() == source.read_bytes()
        print("IMAGE_EMBEDDED_MODEL_OFFLINE_FIXTURE_PASS")
    except BaseException:
        for item in OUT.iterdir():
            item.unlink()
        OUT.rmdir()
        raise

if __name__ == "__main__":
    make()
