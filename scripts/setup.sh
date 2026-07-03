#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  python -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f configs/settings.toml ]; then
  cp configs/settings.example.toml configs/settings.toml
  echo "Created configs/settings.toml from example. Please edit paths for your PGX environment."
fi

echo "Setup complete."
echo "Next: edit configs/settings.toml, then run scripts/start.sh"
