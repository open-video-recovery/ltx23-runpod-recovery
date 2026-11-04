#!/usr/bin/env python3
"""Audit an original LTX 2.3 I2V API workflow; do not invent one."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

ORIGINAL_SHA = "5af9645230f38e41e5f9e8ed1946f206732cf236ab54b535a71443ca40a2e761"
REQUIRED = {
    "316": "CheckpointLoaderSimple",
    "285": "LoraLoaderModelOnly",
    "296": "LTXVImgToVideoInplace",
    "288": "LTXVImgToVideoInplace",
}
STAGE_1 = "1.0, 0.99375, 0.9875, 0.98125, 0.975, 0.909375, 0.725, 0.421875, 0.0"
STAGE_2 = "0.85, 0.7250, 0.4219, 0.0"


def inspect(source: Path) -> dict:
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    graph = json.loads(data)
    if not isinstance(graph, dict):
        raise ValueError("NOT_API_GRAPH_JSON")
    for identifier, name in REQUIRED.items():
        if graph.get(identifier, {}).get("class_type") != name:
            raise ValueError(f"MISSING_NODE:{identifier}:{name}")
    if graph.get("306", {}).get("inputs", {}).get("sigmas") != STAGE_1:
        raise ValueError("FIRST_STAGE_SIGMA_DRIFT")
    if graph.get("281", {}).get("inputs", {}).get("sigmas") != STAGE_2:
        raise ValueError("REFINE_STAGE_SIGMA_DRIFT")
    return {"sha256": digest, "original_exact_match": digest == ORIGINAL_SHA, "nodes": len(graph), "structure": "PASS"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path)
    args = parser.parse_args()
    print(json.dumps(inspect(args.file), indent=2))
