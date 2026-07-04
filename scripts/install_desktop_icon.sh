#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"
DESKTOP_FILE_NAME="Musubi_LoRA_Factory.desktop"
DESKTOP_FILE="$DESKTOP_DIR/$DESKTOP_FILE_NAME"
APP_FILE="$APPLICATIONS_DIR/$DESKTOP_FILE_NAME"
LAUNCHER="$APP_DIR/scripts/start_desktop_icon.sh"
ICON_DIR="$APP_DIR/assets/icons"
PNG_ICON_FILE="$ICON_DIR/musubi_lora_factory.png"
SVG_ICON_FILE="$ICON_DIR/musubi_lora_factory.svg"
ICON_B64="$APP_DIR/assets/musubi_lora_factory_icon_64.png.b64"
ICON_FILE="$SVG_ICON_FILE"

mkdir -p "$DESKTOP_DIR" "$APPLICATIONS_DIR" "$APP_DIR/logs" "$ICON_DIR"
chmod +x "$APP_DIR/scripts/start.sh" "$LAUNCHER"

if [ -f "$ICON_B64" ]; then
  if base64 --decode --ignore-garbage "$ICON_B64" > "$PNG_ICON_FILE" 2>/dev/null; then
    chmod 644 "$PNG_ICON_FILE"
    ICON_FILE="$PNG_ICON_FILE"
  else
    rm -f "$PNG_ICON_FILE"
    echo "WARN: PNG icon decode failed. Falling back to SVG icon: $SVG_ICON_FILE"
  fi
else
  echo "WARN: PNG icon base64 asset not found: $ICON_B64"
fi

if [ ! -f "$ICON_FILE" ]; then
  echo "ERROR: icon file not found: $ICON_FILE"
  exit 1
fi

cat > "$APP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Musubi LoRA Factory
Comment=Launch Musubi LoRA Factory GUI
Exec=$LAUNCHER
Path=$APP_DIR
Icon=$ICON_FILE
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
echo "Icon: $ICON_FILE"
echo "If GNOME asks, right-click the icon and choose 'Allow Launching'."
echo "If launch fails, check: $APP_DIR/logs/desktop_launcher.log"
