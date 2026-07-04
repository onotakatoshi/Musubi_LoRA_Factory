#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Running scripts/setup.sh first..."
  bash ./scripts/setup.sh
fi

source .venv/bin/activate
python app/fix_local_paths.py
