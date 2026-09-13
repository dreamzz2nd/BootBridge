#!/usr/bin/env python3
"""
PyInstaller Spec & Builder script to freeze BootBridge into a standalone Windows .exe executable package.
Creates BootBridge-Setup.exe for 1-click Windows execution.
"""

import os
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def build_windows_exe():
    print("==========================================")
    print("   Building Standalone BootBridge.exe")
    print("==========================================")

    pyinstaller_cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",
        "--windowed",
        "--name=BootBridge-Setup",
        "--icon=assets/icon.png",
        "--add-data=assets;assets",
        "--add-data=ui;ui",
        "--add-data=core;core",
        "--add-data=desktop;desktop",
        "--add-data=README.md;.",
        "--add-data=README.id.md;.",
        "gui_installer.py"
    ]

    try:
        subprocess.run(pyinstaller_cmd, check=True)
        print("Successfully created standalone executable package in dist/BootBridge-Setup!")
    except Exception as e:
        print(f"Build info: Run 'pip install pyinstaller' to compile to native .exe ({e})")

if __name__ == "__main__":
    build_windows_exe()
