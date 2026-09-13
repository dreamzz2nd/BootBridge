#!/usr/bin/env python3
"""
BootBridge Graphical Installer (GUI Setup Wizard)
Universal entry-point that launches the Modern Setup Wizard.
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def main():
    # Prefer Modern Tkinter-based Setup Wizard for zero-dependency universal launch
    try:
        from setup_wizard import main as wizard_main
        wizard_main()
        return
    except Exception as e:
        print(f"[Setup Wizard] Tkinter launcher fallback: {e}")

    # Fallback to GTK3 if available
    try:
        import gi
        gi.require_version('Gtk', '3.0')
        from gi.repository import Gtk
        print("[Setup Wizard] Launching GTK3 Setup Fallback...")
    except Exception as e:
        print(f"[Setup Wizard] Could not initialize GUI: {e}")
        print("Please ensure Python with Tkinter or GTK3 is installed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
