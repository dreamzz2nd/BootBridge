#!/usr/bin/env bash
# BootBridge Release Packager Script for Windows, macOS, and Linux (.exe, .dmg, .deb, .zip)
set -e

VERSION="1.0.0"
DIST_DIR="dist"

echo "==================================================="
echo "    BootBridge Multi-Platform Packager v${VERSION}"
echo "==================================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/win_pkg" "$DIST_DIR/mac_pkg" "$DIST_DIR/linux_pkg" "$DIST_DIR/universal_pkg"

COMMON_FILES="bootbridge.py setup_wizard.py gui_installer.py install.sh start.sh bootbridge_installer.bat bootbridge_installer_mac.command Install_BootBridge.desktop core ui assets desktop README.md README.id.md LICENSE"

echo "[1/5] Copying platform package assets..."
cp -r $COMMON_FILES "$DIST_DIR/win_pkg/"
cp -r $COMMON_FILES "$DIST_DIR/mac_pkg/"
cp -r $COMMON_FILES "$DIST_DIR/linux_pkg/"
cp -r $COMMON_FILES "$DIST_DIR/universal_pkg/"

# Ensure execution permissions on scripts
chmod +x "$DIST_DIR/mac_pkg/bootbridge_installer_mac.command"
chmod +x "$DIST_DIR/linux_pkg/install.sh"
chmod +x "$DIST_DIR/linux_pkg/start.sh"
chmod +x "$DIST_DIR/linux_pkg/setup_wizard.py"

echo "[2/5] Building Windows Standalone Package..."
cd "$DIST_DIR/win_pkg"
zip -r -q "../BootBridge-v${VERSION}-Windows-Package.zip" .
cd "$SCRIPT_DIR"

echo "[3/5] Building macOS Package (.dmg & .zip)..."
cd "$DIST_DIR/mac_pkg"
zip -r -q "../BootBridge-v${VERSION}-macOS-Package.zip" .
cd "$SCRIPT_DIR"
if [ -f "installer/macos/build_dmg.sh" ] && [ "$(uname)" == "Darwin" ]; then
    bash installer/macos/build_dmg.sh
fi

echo "[4/5] Building Linux Packages (.deb & .tar.gz)..."
cd "$DIST_DIR/linux_pkg"
tar -czf "../BootBridge-v${VERSION}-Linux-x64-Package.tar.gz" .
cd "$SCRIPT_DIR"
if [ -f "installer/linux/build_deb.sh" ]; then
    bash installer/linux/build_deb.sh || echo "Warning: dpkg-deb build skipped on non-debian host"
fi

cd "$DIST_DIR/universal_pkg"
zip -r -q "../BootBridge-v${VERSION}-Universal-All-OS.zip" .
cd "$SCRIPT_DIR"

echo "[5/5] Finalizing Distribution Artifacts..."
echo "==================================================="
echo "Packages Built Successfully inside 'dist/':"
ls -lh "$DIST_DIR"
