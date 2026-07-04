#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DESKTOP_FILE_NAME="Musubi_LoRA_Factory.desktop"
DESKTOP_FILE="$DESKTOP_DIR/$DESKTOP_FILE_NAME"
APP_FILE="$APPLICATIONS_DIR/$DESKTOP_FILE_NAME"
LAUNCHER="$APP_DIR/scripts/start_desktop_icon.sh"

mkdir -p "$DESKTOP_DIR" "$APPLICATIONS_DIR" "$APP_DIR/logs"
chmod +x "$APP_DIR/scripts/start.sh" "$LAUNCHER"

cat > "$APP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Musubi LoRA Factory
Comment=Launch Musubi LoRA Factory GUI
Exec=$LAUNCHER
Path=$APP_DIR
Terminal=false
Categories=Development;Graphics;Utility;
StartupNotify=true
EOF

cp "$APP_FILE" "$DESKTOP_FILE"
chmod +x "$APP_FILE" "$DESKTOP_FILE"

if command -v gio >/dev/null 2>&1; then
  gio set "$DESKTOP_FILE" metadata::trusted true >/dev/null 2>&1 || true
fi

if command -v update-desktop-database >/dev/null 2>&1; then
  update-desktop-database "$APPLICATIONS_DIR" >/dev/null 2>&1 || true
fi

echo "OK: Desktop icon created: $DESKTOP_FILE"
echo "If GNOME asks, right-click the icon and choose 'Allow Launching'."
echo "If launch fails, check: $APP_DIR/logs/desktop_launcher.log"
