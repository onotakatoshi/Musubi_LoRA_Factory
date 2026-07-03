#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Running scripts/setup.sh first..."
  ./scripts/setup.sh
fi

if [ ! -f configs/settings.toml ]; then
  if [ -f configs/settings.example.toml ]; then
    cp configs/settings.example.toml configs/settings.toml
    echo "Created configs/settings.toml from example. Open the Settings tab and set your PGX paths."
  else
    echo "configs/settings.example.toml not found. Cannot create settings.toml."
    exit 1
  fi
fi

source .venv/bin/activate
python app/startup_check.py
python app/desktop_main.py
