#!/usr/bin/env bash
# BootBridge Linux .DEB Package Builder
# Constructs the Debian package structure and invokes dpkg-deb
set -e

VERSION="1.0.0"
APP_NAME="bootbridge"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
ROOT_DIR="$( cd "$SCRIPT_DIR/../.." &> /dev/null && pwd )"
DIST_DIR="$ROOT_DIR/dist"
PKG_DIR="$DIST_DIR/deb_pkg/${APP_NAME}_${VERSION}_all"
DEB_OUTPUT="$DIST_DIR/${APP_NAME}_${VERSION}_all.deb"

echo "==================================================="
echo "    BootBridge Linux .DEB Builder v${VERSION}"
echo "==================================================="

# Clean previous build
rm -rf "$DIST_DIR/deb_pkg" "$DEB_OUTPUT"

# Setup directory hierarchy
mkdir -p "$PKG_DIR/DEBIAN"
mkdir -p "$PKG_DIR/opt/bootbridge"
mkdir -p "$PKG_DIR/usr/bin"
mkdir -p "$PKG_DIR/usr/share/applications"
mkdir -p "$PKG_DIR/usr/share/icons/hicolor/128x128/apps"
mkdir -p "$PKG_DIR/usr/share/doc/bootbridge"

echo "[1/4] Copying package control scripts..."
cp "$SCRIPT_DIR/control" "$PKG_DIR/DEBIAN/control"
cp "$SCRIPT_DIR/postinst" "$PKG_DIR/DEBIAN/postinst"
cp "$SCRIPT_DIR/prerm" "$PKG_DIR/DEBIAN/prerm"
chmod 755 "$PKG_DIR/DEBIAN/postinst" "$PKG_DIR/DEBIAN/prerm"

echo "[2/4] Copying application code to /opt/bootbridge..."
cp -r "$ROOT_DIR/bootbridge.py" \
      "$ROOT_DIR/setup_wizard.py" \
      "$ROOT_DIR/gui_installer.py" \
      "$ROOT_DIR/core" \
      "$ROOT_DIR/ui" \
      "$ROOT_DIR/assets" \
      "$ROOT_DIR/desktop" \
      "$PKG_DIR/opt/bootbridge/"

# Copy documentation
cp "$ROOT_DIR/README.md" "$ROOT_DIR/README.id.md" "$ROOT_DIR/LICENSE" "$PKG_DIR/usr/share/doc/bootbridge/"

echo "[3/4] Creating system launchers and desktop integration..."
# Launcher in /usr/bin/bootbridge
cat << 'EOF' > "$PKG_DIR/usr/bin/bootbridge"
#!/usr/bin/env bash
exec python3 /opt/bootbridge/bootbridge.py "$@"
EOF
chmod 755 "$PKG_DIR/usr/bin/bootbridge"

# Setup wizard launcher /usr/bin/bootbridge-setup
cat << 'EOF' > "$PKG_DIR/usr/bin/bootbridge-setup"
#!/usr/bin/env bash
exec python3 /opt/bootbridge/setup_wizard.py "$@"
EOF
chmod 755 "$PKG_DIR/usr/bin/bootbridge-setup"

# Desktop entry in /usr/share/applications/
cat << 'EOF' > "$PKG_DIR/usr/share/applications/bootbridge.desktop"
[Desktop Entry]
Name=BootBridge
GenericName=Physical Windows VM Launcher
Comment=Safe & Lightweight Dual-Boot Windows Virtualization for Linux
Exec=/usr/bin/bootbridge
Icon=bootbridge
Terminal=false
Type=Application
Categories=System;Utility;Emulator;
Keywords=Virtualization;QEMU;DualBoot;Windows;KVM;
EOF

# Icon in /usr/share/icons/hicolor/128x128/apps/bootbridge.png
if [ -f "$ROOT_DIR/assets/bootbridge.png" ]; then
    cp "$ROOT_DIR/assets/bootbridge.png" "$PKG_DIR/usr/share/icons/hicolor/128x128/apps/bootbridge.png"
fi

echo "[4/4] Building .DEB package using dpkg-deb..."
if command -v dpkg-deb &> /dev/null; then
    dpkg-deb --build --root-owner-group "$PKG_DIR" "$DEB_OUTPUT"
    echo "[✔] Debian package created successfully: $DEB_OUTPUT"
else
    echo "[!] dpkg-deb not found. The debian directory structure is ready in $PKG_DIR"
fi

echo "==================================================="
echo "Linux .DEB Packaging Completed!"
echo "==================================================="
