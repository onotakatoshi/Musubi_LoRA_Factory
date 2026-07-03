#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Run bash ./scripts/setup.sh first."
  exit 1
fi

if [ $# -lt 1 ]; then
  echo "Usage: bash ./scripts/validation_report.sh /path/to/output_dir [output_name]"
  exit 2
fi

source .venv/bin/activate
python app/validation_report.py "$1" --name "${2:-}"
