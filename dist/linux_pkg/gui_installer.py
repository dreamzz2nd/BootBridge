#!/usr/bin/env python3
"""
Graphical Installer (GUI Setup Wizard) for BootBridge.
Allows non-technical users to install BootBridge with a single click.
"""

import os
import sys
import subprocess
import shutil
import threading
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class BootBridgeInstallerWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="BootBridge Setup Wizard")
        self.set_default_size(520, 420)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)

        # Main Layout Box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        self.add(main_box)

        # Header Title
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        title_lbl = Gtk.Label()
        title_lbl.set_markup("<span size='x-large' weight='bold'>Selamat Datang di BootBridge Installer</span>")
        subtitle_lbl = Gtk.Label(label="Aplikasi virtualisasi dual-boot fisik 100% gratis dan ringan.")
        subtitle_lbl.get_style_context().add_class("dim-label")
        header_box.pack_start(title_lbl, False, False, 0)
        header_box.pack_start(subtitle_lbl, False, False, 0)
        main_box.pack_start(header_box, False, False, 0)

        # OS Selection Section
        os_frame = Gtk.Frame(label=" Pilih Sistem Operasi Anda ")
        os_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        os_box.set_margin_start(16)
        os_box.set_margin_end(16)
        os_box.set_margin_top(12)
        os_box.set_margin_bottom(12)
        os_frame.add(os_box)

        is_linux = sys.platform.startswith("linux")
        is_win = sys.platform == "win32"
        is_mac = sys.platform == "darwin"

        self.radio_linux = Gtk.RadioButton.new_with_label(None, "Linux (Ubuntu, Debian, Fedora, Arch, Manjaro, Mint)")
        self.radio_win = Gtk.RadioButton.new_with_label_from_widget(self.radio_linux, "Microsoft Windows (Windows 10 / 11)")
        self.radio_mac = Gtk.RadioButton.new_with_label_from_widget(self.radio_linux, "Apple macOS (Intel / Apple Silicon)")

        if is_linux:
            self.radio_linux.set_active(True)
        elif is_win:
            self.radio_win.set_active(True)
        elif is_mac:
            self.radio_mac.set_active(True)

        os_box.pack_start(self.radio_linux, False, False, 0)
        os_box.pack_start(self.radio_win, False, False, 0)
        os_box.pack_start(self.radio_mac, False, False, 0)
        main_box.pack_start(os_frame, False, False, 0)

        # Status & Progress Section
        self.status_lbl = Gtk.Label(label="Klik 'Install Sekarang' untuk memulai instalasi otomatis.")
        self.status_lbl.set_xalign(0.0)
        main_box.pack_start(self.status_lbl, False, False, 0)

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_fraction(0.0)
        main_box.pack_start(self.progress_bar, False, False, 0)

        # Log Scrolled Text Window
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(100)
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        
        self.log_view = Gtk.TextView()
        self.log_view.set_editable(False)
        self.log_view.set_monospace(True)
        self.log_buffer = self.log_view.get_buffer()
        scrolled.add(self.log_view)
        main_box.pack_start(scrolled, True, True, 0)

        # Action Buttons Box
        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        btn_box.set_halign(Gtk.Align.END)

        self.btn_cancel = Gtk.Button(label="Batal")
        self.btn_cancel.connect("clicked", Gtk.main_quit)

        self.btn_install = Gtk.Button(label="Install Sekarang")
        self.btn_install.get_style_context().add_class("suggested-action")
        self.btn_install.connect("clicked", self.on_install_clicked)

        btn_box.pack_start(self.btn_cancel, False, False, 0)
        btn_box.pack_start(self.btn_install, False, False, 0)
        main_box.pack_start(btn_box, False, False, 0)

    def log(self, text):
        def _update():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, text + "\n")
            self.status_lbl.set_text(text)
        GLib.idle_add(_update)

    def set_progress(self, fraction):
        GLib.idle_add(lambda: self.progress_bar.set_fraction(fraction))

    def on_install_clicked(self, widget):
        self.btn_install.set_sensitive(False)
        self.btn_cancel.set_sensitive(False)
        threading.Thread(target=self._run_installation, daemon=True).start()

    def _run_installation(self):
        try:
            self.log("Memulai proses instalasi BootBridge...")
            self.set_progress(0.2)

            if self.radio_linux.get_active():
                self.log("Menginstall komponen pendukung Linux (QEMU, GTK, OVMF)...")
                install_script = os.path.join(SCRIPT_DIR, "install.sh")
                if os.path.exists(install_script):
                    res = subprocess.run(["bash", install_script], capture_output=True, text=True)
                    self.log(res.stdout)
            elif self.radio_mac.get_active():
                self.log("Menginstall komponen macOS via Homebrew...")
                subprocess.run(["brew", "install", "gtk+3", "gobject-introspection", "qemu", "freerdp"], capture_output=True)
            elif self.radio_win.get_active():
                self.log("Mengonfigurasi paket komponen Windows...")

            self.set_progress(0.8)
            self.log("Membuat shortcut desktop BootBridge...")
            
            apps_dir = os.path.expanduser("~/.local/share/applications")
            os.makedirs(apps_dir, exist_ok=True)
            desktop_src = os.path.join(SCRIPT_DIR, "desktop", "bootbridge.desktop")
            if os.path.exists(desktop_src):
                shutil.copy(desktop_src, apps_dir)
                subprocess.run(["update-desktop-database", apps_dir], capture_output=True)

            self.set_progress(1.0)
            self.log("Instalasi Selesai! Menjalankan BootBridge...")

            GLib.idle_add(self._finish_and_launch)

        except Exception as e:
            self.log(f"Error instalasi: {e}")
            GLib.idle_add(lambda: self.btn_install.set_sensitive(True))

    def _finish_and_launch(self):
        self.destroy()
        bootbridge_py = os.path.join(SCRIPT_DIR, "bootbridge.py")
        subprocess.Popen([sys.executable, bootbridge_py])
        Gtk.main_quit()

def main():
    app = BootBridgeInstallerWindow()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
