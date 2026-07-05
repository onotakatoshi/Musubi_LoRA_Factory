#!/usr/bin/env bash
set -u -o pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MODELS_DIR="${MODELS_DIR:-$HOME/models}"
LOG_DIR="$ROOT_DIR/logs/model_downloads"
DRY_RUN=0
CONTINUE_ON_ERROR=1
SYNC_SETTINGS=1
TARGETS=()

mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/download_$(date +%Y%m%d_%H%M%S).log"

# High-confidence repositories used by current app defaults or common upstream distribution names.
# Some Hugging Face repos are gated. Run `hf auth login` first and accept the model license on Hugging Face.
declare -A REPO DEST NOTE

REPO[z-image]="Tongyi-MAI/Z-Image"
DEST[z-image]="$MODELS_DIR/z-image/Tongyi-MAI/Z-Image"
NOTE[z-image]="Z-Image / Z-Image-Turbo"

REPO[wan22-t2v-a14b]="Wan-AI/Wan2.2-T2V-A14B"
DEST[wan22-t2v-a14b]="$MODELS_DIR/wan/Wan2.2-T2V-A14B"
NOTE[wan22-t2v-a14b]="Wan2.2 T2V-A14B"

REPO[wan22-i2v-a14b]="Wan-AI/Wan2.2-I2V-A14B"
DEST[wan22-i2v-a14b]="$MODELS_DIR/wan/Wan2.2-I2V-A14B"
NOTE[wan22-i2v-a14b]="Wan2.2 I2V-A14B"

REPO[wan22-ti2v-5b]="Wan-AI/Wan2.2-TI2V-5B"
DEST[wan22-ti2v-5b]="$MODELS_DIR/wan/Wan2.2-TI2V-5B"
NOTE[wan22-ti2v-5b]="Wan2.2 TI2V-5B"

REPO[wan21-t2v-14b]="Wan-AI/Wan2.1-T2V-14B"
DEST[wan21-t2v-14b]="$MODELS_DIR/wan/Wan2.1-T2V-14B"
NOTE[wan21-t2v-14b]="Wan2.1 T2V-14B"

REPO[qwen-image]="Qwen/Qwen-Image"
DEST[qwen-image]="$MODELS_DIR/qwen/Qwen-Image"
NOTE[qwen-image]="Qwen-Image"

REPO[hunyuan-video]="tencent/HunyuanVideo"
DEST[hunyuan-video]="$MODELS_DIR/hunyuan-video/HunyuanVideo"
NOTE[hunyuan-video]="HunyuanVideo"

REPO[flux-kontext]="black-forest-labs/FLUX.1-Kontext-dev"
DEST[flux-kontext]="$MODELS_DIR/flux/FLUX.1-Kontext-dev"
NOTE[flux-kontext]="FLUX.1 Kontext dev; gated license may be required"

REPO[flux2-dev]="black-forest-labs/FLUX.2-dev"
DEST[flux2-dev]="$MODELS_DIR/flux/FLUX.2-dev"
NOTE[flux2-dev]="FLUX.2 dev; gated license may be required"

REPO[flux2-klein]="black-forest-labs/FLUX.2-klein"
DEST[flux2-klein]="$MODELS_DIR/flux/FLUX.2-klein"
NOTE[flux2-klein]="FLUX.2 klein; gated license may be required"

usage() {
  cat <<'USAGE'
Usage:
  bash scripts/download_model_assets.sh [target ...] [options]

Targets:
  core              z-image + Wan2.2 T2V + Wan2.2 I2V
  wan22-all         Wan2.2 T2V-A14B + I2V-A14B + TI2V-5B
  all-known         Download every repo currently registered in this script

  z-image
  wan22-t2v-a14b
  wan22-i2v-a14b
  wan22-ti2v-5b
  wan21-t2v-14b
  qwen-image
  hunyuan-video
  flux-kontext
  flux2-dev
  flux2-klein

Options:
  --models-dir DIR    Download root. Default: $HOME/models
  --dry-run           Show commands without downloading
  --stop-on-error     Stop when one model fails
  --no-sync-settings  Do not update configs/settings.toml after downloads
  -h, --help          Show this help

Examples:
  bash scripts/download_model_assets.sh core
  bash scripts/download_model_assets.sh wan22-all
  bash scripts/download_model_assets.sh all-known --models-dir /mnt/models

Before gated downloads:
  hf auth login

Notes:
  - Downloads can be very large. Wan2.2 A14B repos alone are over 100GB each.
  - If a gated Hugging Face repo fails, open its model page in a browser, accept the license, run `hf auth login`, then rerun this script.
  - This script keeps downloading the next target when one target fails, unless --stop-on-error is used.
  - After downloads, this script updates configs/settings.toml from the downloaded files unless --no-sync-settings is used.
USAGE
}

log() {
  echo -e "$*" | tee -a "$LOG_FILE"
}

have_target() {
  [[ -n "${REPO[$1]:-}" ]]
}

add_target() {
  local target="$1"
  case "$target" in
    core)
      TARGETS+=(z-image wan22-t2v-a14b wan22-i2v-a14b)
      ;;
    wan22-all)
      TARGETS+=(wan22-t2v-a14b wan22-i2v-a14b wan22-ti2v-5b)
      ;;
    all-known)
      TARGETS+=(z-image wan22-t2v-a14b wan22-i2v-a14b wan22-ti2v-5b wan21-t2v-14b qwen-image hunyuan-video flux-kontext flux2-dev flux2-klein)
      ;;
    *)
      if have_target "$target"; then
        TARGETS+=("$target")
      else
        log "ERROR: unknown target: $target"
        usage
        exit 2
      fi
      ;;
  esac
}

ensure_hf_cli() {
  if command -v hf >/dev/null 2>&1; then
    HF_CMD=(hf download)
    return 0
  fi
  if command -v huggingface-cli >/dev/null 2>&1; then
    HF_CMD=(huggingface-cli download)
    return 0
  fi
  log "hf command was not found. Installing huggingface_hub CLI for current Python..."
  python3 -m pip install -U "huggingface_hub[cli]" | tee -a "$LOG_FILE"
  if command -v hf >/dev/null 2>&1; then
    HF_CMD=(hf download)
    return 0
  fi
  if command -v huggingface-cli >/dev/null 2>&1; then
    HF_CMD=(huggingface-cli download)
    return 0
  fi
  log "ERROR: hf/huggingface-cli is still not available."
  exit 1
}

unique_targets() {
  local seen=" "
  local out=()
  local t
  for t in "${TARGETS[@]}"; do
    if [[ "$seen" != *" $t "* ]]; then
      out+=("$t")
      seen+="$t "
    fi
  done
  TARGETS=("${out[@]}")
}

download_one() {
  local target="$1"
  local repo="${REPO[$target]}"
  local dest="${DEST[$target]}"
  local note="${NOTE[$target]}"

  log ""
  log "============================================================"
  log "Target: $target"
  log "Name:   $note"
  log "Repo:   $repo"
  log "Dest:   $dest"
  log "============================================================"

  mkdir -p "$dest"

  local cmd=("${HF_CMD[@]}" "$repo" --local-dir "$dest")
  log "Command: ${cmd[*]}"

  if [[ "$DRY_RUN" == "1" ]]; then
    return 0
  fi

  "${cmd[@]}" 2>&1 | tee -a "$LOG_FILE"
  local status=${PIPESTATUS[0]}
  if [[ "$status" != "0" ]]; then
    log "ERROR: download failed for $target, exit=$status"
    if [[ "$CONTINUE_ON_ERROR" != "1" ]]; then
      exit "$status"
    fi
    return "$status"
  fi
  log "OK: downloaded $target"
  return 0
}

sync_settings() {
  if [[ "$SYNC_SETTINGS" != "1" ]]; then
    return 0
  fi
  if [[ "$DRY_RUN" == "1" ]]; then
    log "Dry run: skip settings sync."
    return 0
  fi
  log ""
  log "============================================================"
  log "Sync downloaded model paths into configs/settings.toml"
  log "============================================================"
  python3 "$ROOT_DIR/scripts/sync_model_paths.py" --models-dir "$MODELS_DIR" 2>&1 | tee -a "$LOG_FILE"
  local status=${PIPESTATUS[0]}
  if [[ "$status" != "0" ]]; then
    log "ERROR: settings sync failed, exit=$status"
    if [[ "$CONTINUE_ON_ERROR" != "1" ]]; then
      exit "$status"
    fi
  fi
}

print_summary() {
  log ""
  log "Download log: $LOG_FILE"
  log "Model root:   $MODELS_DIR"
  log ""
  log "Next app steps:"
  log "  cd $ROOT_DIR"
  log "  bash ./scripts/start.sh"
  log "  設定 -> Target model を選択 -> 設定を確認"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --models-dir)
      shift
      if [[ $# -eq 0 ]]; then
        echo "ERROR: --models-dir requires a path" >&2
        exit 2
      fi
      MODELS_DIR="$1"
      ;;
    --dry-run)
      DRY_RUN=1
      ;;
    --stop-on-error)
      CONTINUE_ON_ERROR=0
      ;;
    --no-sync-settings)
      SYNC_SETTINGS=0
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      add_target "$1"
      ;;
  esac
  shift
done

if [[ "${#TARGETS[@]}" -eq 0 ]]; then
  usage
  exit 0
fi

# Rebuild destination paths if --models-dir was passed after declarations.
DEST[z-image]="$MODELS_DIR/z-image/Tongyi-MAI/Z-Image"
DEST[wan22-t2v-a14b]="$MODELS_DIR/wan/Wan2.2-T2V-A14B"
DEST[wan22-i2v-a14b]="$MODELS_DIR/wan/Wan2.2-I2V-A14B"
DEST[wan22-ti2v-5b]="$MODELS_DIR/wan/Wan2.2-TI2V-5B"
DEST[wan21-t2v-14b]="$MODELS_DIR/wan/Wan2.1-T2V-14B"
DEST[qwen-image]="$MODELS_DIR/qwen/Qwen-Image"
DEST[hunyuan-video]="$MODELS_DIR/hunyuan-video/HunyuanVideo"
DEST[flux-kontext]="$MODELS_DIR/flux/FLUX.1-Kontext-dev"
DEST[flux2-dev]="$MODELS_DIR/flux/FLUX.2-dev"
DEST[flux2-klein]="$MODELS_DIR/flux/FLUX.2-klein"

unique_targets
ensure_hf_cli

log "Musubi LoRA Factory model download"
log "Started: $(date)"
log "Dry run: $DRY_RUN"
log "Targets: ${TARGETS[*]}"
log "Models dir: $MODELS_DIR"
log "Sync settings: $SYNC_SETTINGS"

FAILED=0
for target in "${TARGETS[@]}"; do
  if ! download_one "$target"; then
    FAILED=1
  fi
done

sync_settings
print_summary

if [[ "$FAILED" == "1" ]]; then
  log "Result: some downloads failed. Check gated license/auth errors above. Settings sync was still attempted."
  exit 1
fi

log "Result: all requested downloads completed."
