#!/usr/bin/env bash
# BootBridge 1-Click Installer for macOS (Intel & Apple Silicon M1/M2/M3/M4)

set -e

echo "==================================================="
echo "    BootBridge macOS 1-Click Installer v1.0.0"
echo "==================================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

if ! command -v brew &> /dev/null; then
    echo "[!] Homebrew tidak ditemukan. Menginstall Homebrew..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

echo "[1/3] Installing macOS dependencies via Homebrew (GTK3, QEMU, FreeRDP)..."
brew install gtk+3 gobject-introspection qemu freerdp python3 || true

echo "[2/3] Preparing macOS App launcher..."
chmod +x "$SCRIPT_DIR/gui_installer.py" "$SCRIPT_DIR/bootbridge.py"

echo "[3/3] Launching BootBridge Setup Wizard on macOS..."
python3 "$SCRIPT_DIR/gui_installer.py"
