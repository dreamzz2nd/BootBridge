#!/usr/bin/env python3
"""
BootBridge Windows PyInstaller Executable Builder
Creates standalone Windows .exe binaries:
- BootBridge.exe (Main VM & Remote Manager)
- BootBridge-Setup.exe (Standalone Setup Wizard)
"""

import os
import sys
import subprocess
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, "dist")

def ensure_icon_ico():
    ico_path = os.path.join(BASE_DIR, "assets", "icon.ico")
    png_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
    if not os.path.exists(ico_path) and os.path.exists(png_path):
        try:
            from PIL import Image
            img = Image.open(png_path)
            img.save(ico_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
            print("[✔] Generated assets/icon.ico from bootbridge.png")
            return ico_path
        except Exception as e:
            print(f"[!] Pillow not available to convert icon: {e}")
            return None
    elif os.path.exists(ico_path):
        return ico_path
    return None

def build_windows_exe():
    print("===================================================")
    print("   Building Standalone Windows .EXE Packages")
    print("===================================================")

    os.makedirs(DIST_DIR, exist_ok=True)
    icon_path = ensure_icon_ico()

    sep = ";" if sys.platform == "win32" else ":"
    
    add_data = [
        f"--add-data=assets{sep}assets",
        f"--add-data=ui{sep}ui",
        f"--add-data=core{sep}core",
        f"--add-data=desktop{sep}desktop",
        f"--add-data=README.md{sep}.",
        f"--add-data=README.id.md{sep}.",
        f"--add-data=LICENSE{sep}."
    ]

    # 1. Build Standalone Setup Wizard EXE (BootBridge-Setup.exe)
    print("\n[1/2] Compiling Setup Wizard (BootBridge-Setup.exe)...")
    cmd_setup = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=BootBridge-Setup",
        *add_data,
        "setup_wizard.py"
    ]
    if icon_path and os.path.exists(icon_path):
        cmd_setup.append(f"--icon={icon_path}")

    try:
        subprocess.run(cmd_setup, check=True)
        print("[✔] BootBridge-Setup.exe compiled successfully in dist/")
    except Exception as e:
        print(f"[!] Warning during Setup Wizard compilation: {e}")

    # 2. Build Main Application EXE (BootBridge.exe)
    print("\n[2/2] Compiling Main Application (BootBridge.exe)...")
    cmd_app = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name=BootBridge",
        *add_data,
        "bootbridge.py"
    ]
    if icon_path and os.path.exists(icon_path):
        cmd_app.append(f"--icon={icon_path}")

    try:
        subprocess.run(cmd_app, check=True)
        print("[✔] BootBridge.exe compiled successfully in dist/")
    except Exception as e:
        print(f"[!] Warning during Main Application compilation: {e}")

    print("\n===================================================")
    print("Build process completed! Output directory: dist/")
    print("===================================================")

if __name__ == "__main__":
    build_windows_exe()
