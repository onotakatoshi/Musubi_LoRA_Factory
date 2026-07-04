#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$APP_DIR/logs"
mkdir -p "$LOG_DIR"

cd "$APP_DIR"

# Keep the launcher usable when started from a desktop icon where PATH can be minimal.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$PATH"

bash "$APP_DIR/scripts/start.sh" >> "$LOG_DIR/desktop_launcher.log" 2>&1
