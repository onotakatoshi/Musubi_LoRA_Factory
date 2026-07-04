#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

PYTHON_BIN="${PYTHON_BIN:-}"
if [ -z "$PYTHON_BIN" ]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "Python not found. Install it first: sudo apt install -y python3 python3-venv python3-pip"
    exit 1
  fi
fi

if [ ! -d .venv ]; then
  "$PYTHON_BIN" -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f configs/settings.toml ]; then
  cp configs/settings.example.toml configs/settings.toml
  echo "Created configs/settings.toml from example. Please edit paths for your PGX environment."
fi

echo "Setup complete."
echo "Next: edit configs/settings.toml, then run scripts/check.sh and scripts/start.sh"
echo "Optional: run scripts/create_desktop_launcher.sh to create a desktop icon."
