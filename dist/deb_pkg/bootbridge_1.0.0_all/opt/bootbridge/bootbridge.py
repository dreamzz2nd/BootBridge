#!/usr/bin/env python3
"""
BootBridge - Lightweight & Safe Dual-Boot Physical Windows Launcher
Main Application Entry Point (Dual-Engine: GTK3 & Native Universal Tkinter)
"""

import os
import sys

# Support PyInstaller frozen bundle (_MEIPASS) and standard source execution
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

def run_gtk():
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, GLib

    GLib.set_prgname("bootbridge")
    GLib.set_application_name("BootBridge")

    icon_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
    if os.path.exists(icon_path):
        try:
            Gtk.Window.set_default_icon_from_file(icon_path)
        except Exception:
            pass

    from ui.app_window import BootBridgeApp
    app = BootBridgeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.update_dependency_ui()
    Gtk.main()

def run_tkinter():
    from ui.tk_app_window import BootBridgeTkApp
    app = BootBridgeTkApp()
    app.mainloop()

def main():
    # 1. Attempt GTK3 interface first on all platforms (Linux, Windows, macOS)
    try:
        run_gtk()
        return
    except Exception as e:
        print(f"[BootBridge] GTK3 not available ({e}). Launching Universal Native GUI...")

    # 2. Fallback to Universal Native Tkinter GUI
    try:
        run_tkinter()
    except Exception as err:
        print(f"[BootBridge] Fatal error starting UI: {err}")
        sys.exit(1)

if __name__ == "__main__":
    main()
