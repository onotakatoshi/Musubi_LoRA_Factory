#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate

python -m py_compile app/*.py
python app/smoke_test.py

echo "Check OK"
