#!/usr/bin/env python3
"""Generate a provisional full model-bearing Dockerfile in a large build context.

Input: --staging produced by prepare_embedded_bundle.py, containing already
verified four-model chunks. The generated Dockerfile puts each chunk into a
separate OCI layer, preserving the GHCR per-layer size limit. At startup the
worker rebuilds all model files locally (no external model downloads).

* Does not publish, sign off, or test a full GPU image.
* Fails if audited workflows/i2v.json is absent (unless test-only flag).
* Uses our own pinned GHCR ComfyUI/PyTorch engine base, never a retired RirukaChan image.
* For production, the ComfyUI dependency and custom-node stack must be pinned,
  the workflow GPU-tested, and the public legal gate satisfied.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import shutil

from prepare_embedded_bundle import SCHEMA, safe_relpath


def render(staging: Path, project: Path, *, test_only: bool = False, source_repository: str = "open-video-recovery/ltx23-runpod-recovery") -> Path:
    import re
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source_repository):
        raise ValueError("INVALID_IMAGE_SOURCE_REPOSITORY")
    data = json.loads((staging / "bundle.json").read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError("INVALID_STAGING_SCHEMA")
    workflow = project / "workflows" / "i2v.json"
    if not test_only and not workflow.is_file():
        raise ValueError("AUDITED_I2V_WORKFLOW_REQUIRED")
    targets = {
        "runtime": project / "runtime",
        "scripts/model_chunks.py": project / "scripts/model_chunks.py",
        "models.lock.json": project / "models.lock.json",
        "third_party_licenses": project / "third_party_licenses",
        "NOTICE-THIRD-PARTY.md": project / "NOTICE-THIRD-PARTY.md",
        "workflows": project / "workflows",
    }
    for destination, source in targets.items():
        if not source.exists():
            raise FileNotFoundError(str(source))
        out = staging / destination
        if out.exists():
            raise ValueError("STAGING_TARGET_ALREADY_EXISTS:" + destination)
        out.parent.mkdir(parents=True, exist_ok=True)
        if source.is_dir():
            shutil.copytree(source, out)
        else:
            shutil.copyfile(source, out)

    lines = [
        "# GENERATED CANDIDATE: never publish as verified GPU video endpoint.",
        "FROM ghcr.io/open-video-recovery/ltx23-runpod-recovery@sha256:6eddba26842c6f6d02e9f07ef3a409d11eee3b54425e5b7890b1666e1e3aa07e",
        f'LABEL org.opencontainers.image.source="https://github.com/{source_repository}"',
        'LABEL org.opencontainers.image.description="Experimental LTX 2.3 full-model private candidate; NOT video verified"',
        "WORKDIR /opt/recovery",
        "COPY runtime/ runtime/",
        "COPY scripts/model_chunks.py scripts/model_chunks.py",
        "COPY models.lock.json models.lock.json",
        "COPY NOTICE-THIRD-PARTY.md NOTICE-THIRD-PARTY.md",
        "COPY third_party_licenses/ third_party_licenses/",
        "COPY workflows/ workflows/",
        "COPY bundle.json model_bundle/bundle.json",
    ]
    if not isinstance(data.get("models"), list) or not data["models"]:
        raise ValueError("EMPTY_BUNDLE")
    chunk_count = 0
    for entry in data["models"]:
        if not isinstance(entry, dict):
            raise ValueError("INVALID_BUNDLE_ENTRY")
        manifest_rel = safe_relpath(entry["manifest"])
        if manifest_rel.parts[:1] != ("model_chunks",):
            raise ValueError("INVALID_MODEL_CHUNK_PATH")
        doc = json.loads((staging / manifest_rel).read_text(encoding="utf-8"))
        if doc.get("sha256") != entry["sha256"] or doc.get("bytes") != entry["bytes"]:
            raise ValueError("MODEL_MANIFEST_NOT_LOCKED")
        lines.append(f"COPY {manifest_rel.as_posix()} model_bundle/{manifest_rel.as_posix()}")
        for part in doc["parts"]:
            filename = part["name"]
            if not filename.startswith("part-") or not filename.endswith(".bin"):
                raise ValueError("INVALID_CHUNK_FILENAME")
            file_rel = manifest_rel.parent / filename
            if not (staging / file_rel).is_file():
                raise FileNotFoundError(str(file_rel))
            # Each line generates one OCI layer. This is necessary because
            # the original checkpoint can exceed GHCR's 10 GB layer limit.
            lines.append(f"COPY {file_rel.as_posix()} model_bundle/{file_rel.as_posix()}")
            chunk_count += 1
    if not chunk_count:
        raise ValueError("NO_CHUNKS")
    lines.extend([
        "RUN chmod +x /opt/recovery/runtime/start.sh",
        '# All weights included in OCI; at startup restore to /comfyui/models with SHA256',
        'CMD ["/bin/bash", "-lc", "python3 /opt/recovery/runtime/restore_model_bundle.py --bundle-root /opt/recovery/model_bundle --model-root /comfyui/models && exec /opt/recovery/runtime/start.sh"]',
    ])
    output = staging / "Dockerfile.embedded-candidate"
    output.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("DOCKERFILE_CANDIDATE_GENERATED", chunk_count, "separate chunk layers", flush=True)
    return output


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--staging", type=Path, required=True)
    ap.add_argument("--project", type=Path, default=Path(__file__).resolve().parents[1])
    ap.add_argument("--test-only-no-workflow", action="store_true")
    ap.add_argument("--source-repository", default="open-video-recovery/ltx23-runpod-recovery")
    args = ap.parse_args()
    print(render(args.staging, args.project, test_only=args.test_only_no_workflow, source_repository=args.source_repository))
