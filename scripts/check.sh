#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

step() {
  echo
  echo "============================================================"
  echo "$1"
  echo "============================================================"
}

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  exit 1
fi

source .venv/bin/activate

step "1/6 PySide6 import check"
python - <<'PY'
from PySide6.QtWidgets import QApplication
print('PySide6 import OK')
PY

step "2/6 Python syntax check"
python -m py_compile app/*.py

echo "py_compile OK"

step "3/6 Startup structure check"
python app/startup_check.py

step "4/6 Desktop static check"
python app/desktop_static_check.py

step "5/6 Smoke test"
python app/smoke_test.py

step "6/6 Environment check"
python app/env_check.py

echo
echo "Check OK"
echo "Next: ./scripts/start.sh or double-click the desktop icon."
