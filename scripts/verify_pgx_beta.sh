#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

if [ ! -d .venv ]; then
  echo ".venv not found. Running setup first."
  bash ./scripts/setup.sh
fi

source .venv/bin/activate

bash ./scripts/check.sh
bash ./scripts/check_beta.sh
python app/env_check_test.py
python app/docs_static_check.py
python app/verify_pgx_beta_extra_static_check.py
python app/collect_debug_info_static_check.py
python app/validation_report_static_check.py
python app/desktop_launch_static_check.py
python app/create_sample_dataset_static_check.py
python app/desktop_launch_smoke_test.py
python app/verification_readiness.py

echo "PGX beta verification checks passed. You can start GUI validation."
