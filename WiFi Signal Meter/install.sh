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

read -p "Add an autostart entry to launch fullscreen on login? [y/N] " answer
if [[ "$answer" =~ ^[Yy]$ ]]; then
    mkdir -p ~/.config/autostart
    cat > ~/.config/autostart/wifi-meter.desktop <<EOF
[Desktop Entry]
Type=Application
Name=WiFi Signal Meter
Exec=python3 "$SCRIPT_DIR/main.py" --fullscreen
EOF
    echo "Autostart entry written to ~/.config/autostart/wifi-meter.desktop"
fi

echo "Done. Run it now with:"
echo "  python3 \"$SCRIPT_DIR/main.py\""
