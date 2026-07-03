#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate

python app/launcher_check.py
python app/command_preview_test.py
python app/project_roundtrip_test.py
python app/training_engine_test.py
python app/beta_status_test.py
python app/beta_status.py

echo "Beta check OK"
