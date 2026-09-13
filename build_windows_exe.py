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

def build_windows_exe():
    print("===================================================")
    print("   Building Standalone Windows .EXE Packages")
    print("===================================================")

    os.makedirs(DIST_DIR, exist_ok=True)
    icon_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
    
    # Common PyInstaller arguments
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
        "--onedir",
        "--windowed",
        "--name=BootBridge-Setup",
        *add_data,
        "setup_wizard.py"
    ]
    if os.path.exists(icon_path):
        cmd_setup.append(f"--icon={icon_path}")

    try:
        subprocess.run(cmd_setup, check=True)
        print("[✔] BootBridge-Setup.exe compiled successfully in dist/BootBridge-Setup/")
    except Exception as e:
        print(f"[!] Warning during Setup Wizard compilation: {e}")

    # 2. Build Main Application EXE (BootBridge.exe)
    print("\n[2/2] Compiling Main Application (BootBridge.exe)...")
    cmd_app = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onedir",
        "--windowed",
        "--name=BootBridge",
        *add_data,
        "bootbridge.py"
    ]
    if os.path.exists(icon_path):
        cmd_app.append(f"--icon={icon_path}")

    try:
        subprocess.run(cmd_app, check=True)
        print("[✔] BootBridge.exe compiled successfully in dist/BootBridge/")
    except Exception as e:
        print(f"[!] Warning during Main Application compilation: {e}")

    print("\n===================================================")
    print("Build process completed! Output directory: dist/")
    print("===================================================")

if __name__ == "__main__":
    build_windows_exe()
