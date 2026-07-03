#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

echo "Updating Musubi LoRA Factory..."
git pull --ff-only

if [ ! -d .venv ]; then
  echo ".venv not found. Running setup..."
  ./scripts/setup.sh
else
  source .venv/bin/activate
  python -m pip install --upgrade pip
  pip install -r requirements.txt
fi

./scripts/check.sh

echo "Update complete. Run ./scripts/start.sh or use the desktop icon."
