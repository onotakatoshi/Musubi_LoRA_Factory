#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate

python -m py_compile app/desktop_main.py app/commands.py app/command_path_guard.py app/training_engine.py app/musubi_runtime_check.py app/env_check.py app/export_validator.py app/desktop_static_check.py
python app/launcher_check.py
python app/desktop_static_check.py
python app/command_preview_test.py
python app/command_path_guard_test.py
python app/project_roundtrip_test.py
python app/training_engine_test.py
python app/output_detector_test.py
python app/export_validator_test.py
python app/beta_status_test.py
python app/beta_status.py

echo "Beta check OK"
