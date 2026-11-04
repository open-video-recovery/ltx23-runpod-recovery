#!/usr/bin/env bash
set -euo pipefail
if [[ ! -f /opt/recovery/workflows/i2v.json ]]; then
  echo 'Missing audited workflow. This experimental worker cannot generate video.' >&2
  exit 44
fi
python3 /comfyui/main.py --listen 127.0.0.1 --port 8188 --disable-auto-launch --lowvram > /tmp/comfyui.log 2>&1 &
exec python3 /opt/recovery/runtime/worker.py
