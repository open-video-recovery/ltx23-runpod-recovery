"""Independent RunPod -> ComfyUI bridge. EXPERIMENTAL; no GPU proof.

Requires an independently validated API workflow with __INPUT_IMAGE__,
__PROMPT__, __SEED__ placeholders and a SaveVideo output. Does not
contain or reproduce any legacy proprietary Python bytes.
"""
from __future__ import annotations
import base64
import copy
import json
import os
from pathlib import Path
import time
import urllib.parse
import urllib.request
import uuid

URL = os.environ.get("COMFY_URL", "http://127.0.0.1:8188").rstrip("/")
WORKFLOW = Path(os.environ.get("LTX_WORKFLOW_PATH", "/opt/recovery/workflows/i2v.json"))
INPUT = Path(os.environ.get("COMFY_INPUT_ROOT", "/comfyui/input"))
MAX_IMAGE_BYTES = 8 * 1024 * 1024
MAX_VIDEO_BYTES = 19 * 1024 * 1024
MAX_WAIT_SECONDS = 780


def patch_workflow(template: dict, prompt: str, image_name: str, seed: int) -> dict:
    if not isinstance(template, dict) or not template:
        raise ValueError("WORKFLOW_API_JSON_REQUIRED")
    substitutions = {
        "__PROMPT__": prompt,
        "__INPUT_IMAGE__": image_name,
        "__SEED__": seed,
    }
    found = set()

    def replace(value):
        if isinstance(value, str) and value in substitutions:
            found.add(value)
            return substitutions[value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        if isinstance(value, list):
            return [replace(item) for item in value]
        return value

    result = replace(copy.deepcopy(template))
    if not set(substitutions).issubset(found):
        raise ValueError("WORKFLOW_PLACEHOLDERS_MISSING")
    if not any(
        isinstance(node, dict) and node.get("class_type") == "SaveVideo"
        for node in result.values()
    ):
        raise ValueError("WORKFLOW_SAVE_VIDEO_NODE_MISSING")
    return result


def http_json(path: str, payload=None):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        URL + path, data=body, headers={"Content-Type": "application/json"},
        method="POST" if body is not None else "GET",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        if response.status != 200:
            raise RuntimeError(f"COMFY_HTTP_{response.status}")
        return json.loads(response.read(8 * 1024 * 1024))


def output_video(history: dict) -> dict:
    for node in history.get("outputs", {}).values():
        for item in node.get("videos", []):
            if item.get("filename", "").lower().endswith(".mp4"):
                return item
    raise RuntimeError("NO_MP4_IN_COMFY_HISTORY")


def generate(job: dict) -> dict:
    payload = job.get("input") if isinstance(job, dict) else None
    if not isinstance(payload, dict):
        raise ValueError("RUNPOD_INPUT_OBJECT_REQUIRED")
    if payload.get("mode", "i2v") != "i2v":
        raise ValueError("I2V_ONLY")
    image = payload.get("image_base64")
    prompt = payload.get("prompt")
    seed = payload.get("seed", 1234567)
    if not isinstance(prompt, str) or not 1 <= len(prompt) <= 12000:
        raise ValueError("PROMPT_INVALID")
    if not isinstance(seed, int) or isinstance(seed, bool) or not 0 <= seed <= 2**53-1:
        raise ValueError("SEED_INVALID")
    if not isinstance(image, str) or len(image) > MAX_IMAGE_BYTES * 2:
        raise ValueError("IMAGE_INVALID")
    try:
        raw = base64.b64decode(image, validate=True)
    except Exception as exc:
        raise ValueError("IMAGE_BASE64_INVALID") from exc
    if not (0 < len(raw) <= MAX_IMAGE_BYTES) or not (
        raw.startswith(b"\xff\xd8\xff") or raw.startswith(b"\x89PNG\r\n\x1a\n")
    ):
        raise ValueError("INPUT_IMAGE_NOT_JPEG_OR_PNG")
    if not WORKFLOW.is_file():
        raise RuntimeError("I2V_WORKFLOW_NOT_INSTALLED")
    workflow = json.loads(WORKFLOW.read_text(encoding="utf-8"))
    INPUT.mkdir(parents=True, exist_ok=True)
    suffix = ".jpg" if raw.startswith(b"\xff\xd8\xff") else ".png"
    image_name = "recovery-" + uuid.uuid4().hex + suffix
    image_path = INPUT / image_name
    image_path.write_bytes(raw)
    try:
        graph = patch_workflow(workflow, prompt, image_name, seed)
        run_id = uuid.uuid4().hex
        submitted = http_json("/prompt", {"prompt": graph, "client_id": run_id})
        prompt_id = submitted.get("prompt_id")
        if not isinstance(prompt_id, str) or not prompt_id:
            raise RuntimeError("COMFY_PROMPT_REJECTED")
        deadline = time.monotonic() + MAX_WAIT_SECONDS
        while time.monotonic() < deadline:
            history = http_json("/history/" + urllib.parse.quote(prompt_id, safe=""))
            if prompt_id in history:
                record = history[prompt_id]
                if record.get("status", {}).get("status_str") == "error":
                    raise RuntimeError("COMFY_EXECUTION_ERROR")
                video = output_video(record)
                query = urllib.parse.urlencode({
                    key: video.get(key, "") for key in ("filename", "subfolder", "type")
                })
                with urllib.request.urlopen(URL + "/view?" + query, timeout=120) as response:
                    content = response.read(MAX_VIDEO_BYTES + 1)
                if len(content) > MAX_VIDEO_BYTES:
                    raise RuntimeError("VIDEO_TOO_LARGE_USE_OBJECT_STORAGE")
                return {
                    "mime_type": "video/mp4",
                    "video_base64": base64.b64encode(content).decode("ascii"),
                    "prompt_id": prompt_id,
                    "status": "COMPLETED",
                }
            time.sleep(2)
        raise TimeoutError("COMFY_EXECUTION_TIMEOUT")
    finally:
        image_path.unlink(missing_ok=True)


if __name__ == "__main__":
    import runpod
    runpod.serverless.start({"handler": generate})
