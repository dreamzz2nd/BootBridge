#!/usr/bin/env bash
# BootBridge Automatic 1-Click Installer & Launcher
# Works on Linux (Ubuntu, Debian, Fedora, Arch, Manjaro, Mint, etc.)

set -e

echo "=========================================="
echo "    BootBridge 1-Click Installer & Setup"
echo "=========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Install missing system packages on Linux if apt/pacman/dnf is available
if command -v apt &> /dev/null; then
    echo "[1/3] Checking & installing system dependencies (apt)..."
    sudo apt update -qq && sudo apt install -y -qq python3 python3-gi gir1.2-gtk-3.0 qemu-system-x86 ovmf qemu-utils swtpm freerdp2-x11 spice-client-gtk tigervnc-viewer || true
elif command -v pacman &> /dev/null; then
    echo "[1/3] Checking & installing system dependencies (pacman)..."
    sudo pacman -Sy --noconfirm python python-gobject gtk3 qemu-full ovmf swtpm freerdp spice-gtk tigervnc || true
elif command -v dnf &> /dev/null; then
    echo "[1/3] Checking & installing system dependencies (dnf)..."
    sudo dnf install -y python3 python3-gobject gtk3 qemu-system-x86 edk2-ovmf swtpm freerdp spice-gtk-tools tigervnc || true
fi

echo "[2/3] Registering desktop shortcut..."
mkdir -p ~/.local/share/applications
cp "$SCRIPT_DIR/desktop/bootbridge.desktop" ~/.local/share/applications/ 2>/dev/null || true
chmod +x "$SCRIPT_DIR/start.sh" "$SCRIPT_DIR/bootbridge.py"
update-desktop-database ~/.local/share/applications/ 2>/dev/null || true

echo "[3/3] Installation completed successfully!"
echo "Launching BootBridge..."
python3 "$SCRIPT_DIR/bootbridge.py" "$@"
