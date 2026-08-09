#!/usr/bin/env bash
# Memento Lite — single-process launch (API + static frontend).
set -euo pipefail
cd "$(dirname "$0")"

# Optional virtualenv
if [ ! -d venv ]; then
    python3 -m venv venv
fi
# shellcheck disable=SC1091
source venv/bin/activate

pip install -q -r requirements.txt

[ -f .env ] || cp .env.example .env

HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
exec uvicorn backend.main:app --host "$HOST" --port "$PORT"
