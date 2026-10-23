#!/bin/bash
# Installs dependencies and (optionally) an autostart entry for WiFi Signal Meter.
# Run this from inside the extracted package directory on the Raspberry Pi:
#   ./install.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Checking for python3-tk..."
if ! python3 -c "import tkinter" >/dev/null 2>&1; then
    echo "Installing python3-tk..."
    sudo apt update
    sudo apt install -y python3-tk
else
    echo "python3-tk already installed."
fi

write_desktop_entry() {
    # $1 = destination path
    cat > "$1" <<EOF
[Desktop Entry]
Type=Application
Name=WiFi Signal Meter
Comment=Touchscreen WiFi signal strength gauge
Exec=$SCRIPT_DIR/run.sh --fullscreen
Icon=network-wireless
Terminal=false
EOF
    chmod +x "$1"
}

read -p "Add an autostart entry to launch fullscreen on login? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    mkdir -p ~/.config/autostart
    write_desktop_entry ~/.config/autostart/wifi-meter.desktop
    echo "Autostart entry written to ~/.config/autostart/wifi-meter.desktop"
    echo "(it runs via run.sh, which pulls the latest version first if this is a git checkout)"
fi

read -p "Add a desktop icon to launch it manually? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    DESKTOP_DIR="$HOME/Desktop"
    mkdir -p "$DESKTOP_DIR"
    write_desktop_entry "$DESKTOP_DIR/wifi-meter.desktop"
    # Raspberry Pi OS's file manager won't run a .desktop file by double-click
    # until it's marked trusted; do that now so it works immediately.
    if command -v gio >/dev/null 2>&1; then
        gio set "$DESKTOP_DIR/wifi-meter.desktop" "metadata::trusted" true 2>/dev/null || true
    fi
    echo "Desktop icon written to $DESKTOP_DIR/wifi-meter.desktop"
fi

echo "Done. Run it now with:"
echo "  \"$SCRIPT_DIR/run.sh\""
