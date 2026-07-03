#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_DIR="$HOME/Desktop"
APPLICATIONS_DIR="$HOME/.local/share/applications"
LAUNCHER_NAME="Musubi LoRA Factory.desktop"
ICON_PATH="$APP_DIR/assets/icon.png"

mkdir -p "$DESKTOP_DIR" "$APPLICATIONS_DIR"

if [ ! -f "$ICON_PATH" ]; then
  ICON_PATH="utilities-terminal"
fi

cat > "$DESKTOP_DIR/$LAUNCHER_NAME" <<EOF
[Desktop Entry]
Type=Application
Name=Musubi LoRA Factory
Comment=PGX local GUI for musubi-tuner LoRA training
Exec=bash -lc 'cd "$APP_DIR" && ./scripts/start.sh'
Icon=$ICON_PATH
Terminal=true
Categories=Development;Graphics;Utility;
StartupNotify=true
EOF

chmod +x "$DESKTOP_DIR/$LAUNCHER_NAME"
cp "$DESKTOP_DIR/$LAUNCHER_NAME" "$APPLICATIONS_DIR/$LAUNCHER_NAME"
chmod +x "$APPLICATIONS_DIR/$LAUNCHER_NAME"

echo "Desktop launcher created: $DESKTOP_DIR/$LAUNCHER_NAME"
echo "Application launcher created: $APPLICATIONS_DIR/$LAUNCHER_NAME"
echo "If GNOME asks, right-click the desktop icon and choose 'Allow Launching'."
