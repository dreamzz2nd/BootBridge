#!/usr/bin/env bash
# BootBridge macOS .dmg Packager Script
# Assembles BootBridge.app and packages into BootBridge-v1.0.0-macOS.dmg
set -e

VERSION="1.0.0"
APP_NAME="BootBridge"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
DIST_DIR="$ROOT_DIR/dist"
APP_BUNDLE="$DIST_DIR/macos_app/${APP_NAME}.app"
DMG_OUTPUT="$DIST_DIR/${APP_NAME}-v${VERSION}-macOS.dmg"

echo "==================================================="
echo "    BootBridge macOS .DMG Builder v${VERSION}"
echo "==================================================="

# Clean previous build
rm -rf "$DIST_DIR/macos_app" "$DMG_OUTPUT"
mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources" "$APP_BUNDLE/Contents/Frameworks"

echo "[1/4] Assembling ${APP_NAME}.app bundle structure..."
cp "$SCRIPT_DIR/Info.plist" "$APP_BUNDLE/Contents/Info.plist"
echo "APPL????" > "$APP_BUNDLE/Contents/PkgInfo"

# Copy Icon if available (or convert png)
if [ -f "$ROOT_DIR/assets/bootbridge.png" ]; then
    cp "$ROOT_DIR/assets/bootbridge.png" "$APP_BUNDLE/Contents/Resources/bootbridge.png"
fi

# Create launcher script in MacOS
cat << 'EOF' > "$APP_BUNDLE/Contents/MacOS/bootbridge_launcher"
#!/usr/bin/env bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../Resources" &> /dev/null && pwd )"
cd "$DIR"

# Check Python environment
if command -v python3 &> /dev/null; then
    exec python3 "$DIR/bootbridge.py" "$@"
else
    osascript -e 'display dialog "Python 3 is required to run BootBridge. Please install Python 3 or Homebrew." buttons {"OK"} default button "OK" with icon stop'
fi
EOF
chmod +x "$APP_BUNDLE/Contents/MacOS/bootbridge_launcher"

echo "[2/4] Copying BootBridge source code & assets to App Resources..."
cp -r "$ROOT_DIR/bootbridge.py" \
      "$ROOT_DIR/setup_wizard.py" \
      "$ROOT_DIR/gui_installer.py" \
      "$ROOT_DIR/core" \
      "$ROOT_DIR/ui" \
      "$ROOT_DIR/assets" \
      "$ROOT_DIR/desktop" \
      "$ROOT_DIR/README.md" \
      "$ROOT_DIR/README.id.md" \
      "$ROOT_DIR/LICENSE" \
      "$APP_BUNDLE/Contents/Resources/"

echo "[3/4] Preparing DMG staging directory with Applications shortcut..."
DMG_STAGING="$DIST_DIR/dmg_staging"
rm -rf "$DMG_STAGING"
mkdir -p "$DMG_STAGING"
cp -r "$APP_BUNDLE" "$DMG_STAGING/"
ln -s /Applications "$DMG_STAGING/Applications"

echo "[4/4] Building .DMG disk image using hdiutil..."
if command -v hdiutil &> /dev/null; then
    hdiutil create -volname "${APP_NAME}" -srcfolder "$DMG_STAGING" -ov -format UDZO "$DMG_OUTPUT"
    echo "[✔] Successfully generated: $DMG_OUTPUT"
else
    echo "[!] hdiutil is only available on native macOS. Created .app bundle in dist/macos_app/"
fi

rm -rf "$DMG_STAGING"
echo "==================================================="
echo "macOS Packaging Completed!"
echo "==================================================="
