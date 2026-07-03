#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run bash ./scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate
python app/desktop_launch_smoke_test.py
