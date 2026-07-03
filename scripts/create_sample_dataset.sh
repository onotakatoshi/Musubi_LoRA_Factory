#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run bash ./scripts/setup.sh first."
  exit 1
fi

OUT="${1:-sample_data/eye_validation}"
COUNT="${2:-4}"

source .venv/bin/activate
python app/create_sample_dataset.py "$OUT" --count "$COUNT"
