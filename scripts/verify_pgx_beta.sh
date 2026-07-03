#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Running setup first."
  ./scripts/setup.sh
fi

source .venv/bin/activate

./scripts/check.sh
./scripts/check_beta.sh
python app/verification_readiness.py

echo "PGX beta verification checks passed. You can start GUI validation."
