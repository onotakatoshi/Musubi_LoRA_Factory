#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

URL="http://localhost:7865"

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

(
  sleep 3
  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "$URL" >/dev/null 2>&1 || true
  fi
) &

source .venv/bin/activate
python app/main.py
