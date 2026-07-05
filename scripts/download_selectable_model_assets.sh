#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cat <<'MSG'
============================================================
Download assets for all currently selectable Target models
============================================================

This downloads the model repositories currently wired into the normal
Target model list:

  - Z-Image / Z-Image-Turbo
  - Wan2.2 T2V-A14B
  - Wan2.2 I2V-A14B
  - Wan2.2 TI2V-5B
  - Wan2.1 T2V-14B
  - Qwen-Image
  - HunyuanVideo
  - FLUX.1 Kontext dev
  - FLUX.2 dev
  - FLUX.2 klein

Downloads can be very large. Some repositories may require Hugging Face
license approval and `hf auth login` before this script can download them.

MSG

bash "$ROOT_DIR/scripts/download_model_assets.sh" all-known "$@"
STATUS=$?

if [[ "$STATUS" == "0" ]]; then
  echo ""
  echo "============================================================"
  echo "Audit downloaded model assets"
  echo "============================================================"
  python3 "$ROOT_DIR/scripts/audit_model_assets.py"
fi

exit "$STATUS"
