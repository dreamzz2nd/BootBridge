#!/usr/bin/env bash
# BootBridge Release Packager Script
# Bundles BootBridge into clean .zip and .tar.gz standalone packages for release.

set -e

VERSION="1.0.0"
DIST_DIR="dist"
PACKAGE_NAME="BootBridge-v${VERSION}"

echo "=========================================="
echo "    BootBridge Package Builder v${VERSION}"
echo "=========================================="

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR/$PACKAGE_NAME"

echo "[1/3] Copying application files..."
cp -r bootbridge.py gui_installer.py install.sh start.sh Install_BootBridge.desktop \
      core ui assets desktop README.md README.id.md LICENSE "$DIST_DIR/$PACKAGE_NAME/"

# Ensure execution permissions on scripts
chmod +x "$DIST_DIR/$PACKAGE_NAME/start.sh"
chmod +x "$DIST_DIR/$PACKAGE_NAME/install.sh"
chmod +x "$DIST_DIR/$PACKAGE_NAME/gui_installer.py"
chmod +x "$DIST_DIR/$PACKAGE_NAME/bootbridge.py"
chmod +x "$DIST_DIR/$PACKAGE_NAME/Install_BootBridge.desktop"

echo "[2/3] Creating ZIP & TAR.GZ release packages..."
cd "$DIST_DIR"
zip -r -q "${PACKAGE_NAME}-Universal.zip" "$PACKAGE_NAME"
tar -czf "${PACKAGE_NAME}-Linux-x64.tar.gz" "$PACKAGE_NAME"
cd "$SCRIPT_DIR"

echo "[3/3] Packages built successfully inside 'dist/':"
ls -lh "$DIST_DIR"/*.zip "$DIST_DIR"/*.tar.gz
