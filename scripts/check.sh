#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate

python - <<'PY'
from PySide6.QtWidgets import QApplication
print('PySide6 import OK')
PY

python -m py_compile app/*.py
python app/smoke_test.py
python app/env_check.py

echo "Check OK"
