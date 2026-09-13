#!/usr/bin/env python3
"""
BootBridge Universal Multi-Platform Packager
Packages BootBridge for Windows (.exe / .zip), macOS (.dmg / .zip), and Linux (.deb / .tar.gz).
"""

import os
import sys
import shutil
import subprocess
import tarfile
import zipfile

if sys.platform == "win32":
    try:
        if sys.stdout.encoding != 'utf-8':
            sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

VERSION = "1.0.0"
APP_NAME = "BootBridge"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

COMMON_ITEMS = [
    "bootbridge.py",
    "bootbridge.bat",
    "setup_wizard.py",
    "gui_installer.py",
    "install.sh",
    "start.sh",
    "bootbridge_installer.bat",
    "bootbridge_installer_mac.command",
    "Install_BootBridge.desktop",
    "core",
    "ui",
    "assets",
    "desktop",
    "README.md",
    "README.id.md",
    "LICENSE"
]

def make_zip(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                rel_path = os.path.relpath(abs_path, source_dir)
                zf.write(abs_path, rel_path)

def make_targz(source_dir, output_tar):
    with tarfile.open(output_tar, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def package_all():
    print("===================================================")
    print(f"   BootBridge Multi-Platform Packager v{VERSION}")
    print("===================================================")

    os.makedirs(DIST_DIR, exist_ok=True)
    
    # 1. Staging portable packages
    win_stage = os.path.join(DIST_DIR, "win_pkg")
    mac_stage = os.path.join(DIST_DIR, "mac_pkg")
    linux_stage = os.path.join(DIST_DIR, "linux_pkg")
    
    for d in [win_stage, mac_stage, linux_stage]:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.makedirs(d)

    print("\n[1/4] Assembling portable platform archives...")
    for item in COMMON_ITEMS:
        src = os.path.join(BASE_DIR, item)
        if os.path.exists(src):
            for stage in [win_stage, mac_stage, linux_stage]:
                dst = os.path.join(stage, item)
                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)

    # Make standard archives
    make_zip(win_stage, os.path.join(DIST_DIR, f"{APP_NAME}-v{VERSION}-Windows-Package.zip"))
    make_zip(mac_stage, os.path.join(DIST_DIR, f"{APP_NAME}-v{VERSION}-macOS-Package.zip"))
    make_targz(linux_stage, os.path.join(DIST_DIR, f"{APP_NAME}-v{VERSION}-Linux-x64-Package.tar.gz"))
    print("[OK] Portable ZIP and TAR.GZ packages generated.")

    # 2. Linux .DEB Package
    print("\n[2/4] Assembling Linux .DEB Package...")
    deb_script = os.path.join(BASE_DIR, "installer", "linux", "build_deb.sh")
    if os.path.exists(deb_script) and sys.platform.startswith("linux"):
        subprocess.run(["bash", deb_script])
    else:
        print("[Info] Run 'bash installer/linux/build_deb.sh' on Linux to generate .deb")

    # 3. macOS .DMG Package
    print("\n[3/4] Assembling macOS .DMG Package...")
    dmg_script = os.path.join(BASE_DIR, "installer", "macos", "build_dmg.sh")
    if os.path.exists(dmg_script) and sys.platform == "darwin":
        subprocess.run(["bash", dmg_script])
    else:
        print("[Info] Run 'bash installer/macos/build_dmg.sh' on macOS to generate .dmg")

    # 4. Windows .EXE Package
    print("\n[4/4] Assembling Windows .EXE Standalone Package...")
    win_build_script = os.path.join(BASE_DIR, "build_windows_exe.py")
    if os.path.exists(win_build_script) and sys.platform == "win32":
        try:
            from build_windows_exe import build_windows_exe
            build_windows_exe()
        except Exception as e:
            print(f"[Info] PyInstaller builder note: {e}")

    print("\n===================================================")
    print("Packaging finished! Output files in 'dist/':")
    for f in os.listdir(DIST_DIR):
        print(f" - {f}")
    print("===================================================")

if __name__ == "__main__":
    package_all()
