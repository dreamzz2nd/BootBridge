#!/usr/bin/env bash
# BootBridge Startup Script

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install/Update desktop shortcut & icon automatically
mkdir -p ~/.local/share/applications
cp "$SCRIPT_DIR/desktop/bootbridge.desktop" ~/.local/share/applications/ 2>/dev/null || true
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

python3 "$SCRIPT_DIR/bootbridge.py" "$@"

