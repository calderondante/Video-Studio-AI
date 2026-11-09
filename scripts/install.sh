#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export npm_config_cache="${npm_config_cache:-/workspace/.cache/npm}"
export PIP_CACHE_DIR="${PIP_CACHE_DIR:-/workspace/.cache/pip}"
for tool in node npm python3 ffmpeg ffprobe chromium; do command -v "$tool" >/dev/null; done
npm ci --no-audit --no-fund
[ -d .venv ] || python3 -m venv .venv
.venv/bin/pip install -r requirements.lock
npm run typecheck
.venv/bin/python scripts/doctor.py
.venv/bin/python scripts/transcribe.py --check
