#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run scripts/setup.sh first."
  read -r -p "Press Enter to close..." _
  exit 1
fi

if [ ! -f configs/settings.toml ]; then
  echo "configs/settings.toml not found. Run scripts/setup.sh first."
  read -r -p "Press Enter to close..." _
  exit 1
fi

source .venv/bin/activate
python app/desktop_main.py
