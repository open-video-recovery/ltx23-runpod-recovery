"""Safe RunPod Serverless diagnostics image: no model, GPU, or video backend.

A successful diagnostics reply proves that RunPod reached this container;
it does not prove that LTX, ComfyUI, or any video generation is available.
"""
from __future__ import annotations

import json
import sys


def handler(job: dict) -> dict:
    if not isinstance(job, dict) or not isinstance(job.get("input"), dict):
        return {"error": "INPUT_OBJECT_REQUIRED", "build_kind": "diagnostics-only"}
    value = job["input"]
    if value.get("task") != "diagnostics":
        return {"error": "DIAGNOSTICS_ONLY_NO_VIDEO_GENERATION", "ready_for_video": False}
    return {
        "status": "OK",
        "build_kind": "diagnostics-only",
        "ready_for_video": False,
        "has_ltx_models": False,
        "has_workflow": False,
        "gpu_generated": False,
        "message": "The GHCR container and RunPod handler are reachable; video generation is NOT implemented.",
    }


def self_test():
    result = handler({"input": {"task": "diagnostics"}})
    assert result["status"] == "OK"
    assert result["ready_for_video"] is False
    assert result["gpu_generated"] is False
    assert handler({"input": {"task": "generate"}})["error"] == "DIAGNOSTICS_ONLY_NO_VIDEO_GENERATION"
    assert handler({})["error"] == "INPUT_OBJECT_REQUIRED"
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        self_test()
    elif not sys.argv[1:]:
        import runpod
        runpod.serverless.start({"handler": handler})
    else:
        raise SystemExit("Usage: python ghcr_smoke.py [--self-test]")
