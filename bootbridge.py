#!/usr/bin/env python3
"""
BootBridge - Lightweight & Safe Dual-Boot Physical Windows Launcher for Linux
Main Application Entry Point
"""

import os
import sys

# Ensure core package is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.app_window import BootBridgeApp

def main():
    app = BootBridgeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.update_dependency_ui()
    Gtk.main()

if __name__ == "__main__":
    main()
