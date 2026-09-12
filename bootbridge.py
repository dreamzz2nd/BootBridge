#!/usr/bin/env python3
"""
BootBridge - Lightweight & Safe Dual-Boot Physical Windows Launcher for Linux
"""

import os
import sys
import multiprocessing
import subprocess

# Ensure core package is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from core.disk_manager import DiskManager
from core.safety_checker import SafetyChecker
from core.qemu_launcher import QEMULauncher

class BootBridgeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="BootBridge")
        self.set_default_size(780, 680)
        self.set_position(Gtk.WindowPosition.CENTER)

        # State Variables
        self.disks = []
        self.selected_disk = None
        self.deps = SafetyChecker.check_system_dependencies()
        self.launcher = QEMULauncher(log_callback=self.log_message, status_callback=self.on_vm_status_changed)

        # Load Custom CSS Styling
        self.load_css()

        # Build GUI Layout
        self.build_ui()

        # Refresh disk listing on startup
        self.refresh_disks()

    def load_css(self):
        css_path = os.path.join(BASE_DIR, "assets", "style.css")
        if os.path.exists(css_path):
            try:
                provider = Gtk.CssProvider()
                provider.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"[BootBridge] Warning loading CSS: {e}")

    def build_ui(self):
        # HeaderBar
        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.props.title = "BootBridge"
        header.props.subtitle = "Safe & Lightweight Dual-Boot VM Launcher"
        self.set_titlebar(header)

        # Refresh Button
        refresh_btn = Gtk.Button()
        refresh_btn.set_tooltip_text("Refresh Physical Disks")
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_btn.add(refresh_icon)
        refresh_btn.connect("clicked", lambda x: self.refresh_disks())
        header.pack_start(refresh_btn)

        # KVM Status Badge in Header
        self.kvm_badge = Gtk.Label()
        self.update_kvm_badge()
        header.pack_end(self.kvm_badge)

        # Main Outer Scrolled Container
        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(scrolled_window)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        main_box.set_margin_top(16)
        main_box.set_margin_bottom(16)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        scrolled_window.add(main_box)

        # Dependency Warning Card (Visible only if dependencies missing)
        self.dep_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.dep_card.get_style_context().add_class("card")
        self.dep_card.get_style_context().add_class("badge-warning")
        
        dep_title = Gtk.Label(label="⚠️ Dependency System Missing")
        dep_title.set_xalign(0)
        dep_title.get_style_context().add_class("card-title")
        self.dep_card.pack_start(dep_title, False, False, 0)

        self.dep_msg_label = Gtk.Label()
        self.dep_msg_label.set_xalign(0)
        self.dep_msg_label.set_line_wrap(True)
        self.dep_card.pack_start(self.dep_msg_label, False, False, 0)

        dep_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        copy_cmd_btn = Gtk.Button(label="📋 Copy Install Command")
        copy_cmd_btn.connect("clicked", self.copy_install_command)
        dep_btn_box.pack_start(copy_cmd_btn, False, False, 0)
        self.dep_card.pack_start(dep_btn_box, False, False, 0)

        main_box.pack_start(self.dep_card, False, False, 0)
        self.update_dependency_ui()

        # Card 1: Physical Disk Selection
        disk_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        disk_card.get_style_context().add_class("card")

        disk_title = Gtk.Label(label="💾 Physical Storage Drive (Dual-Boot Windows)")
        disk_title.set_xalign(0)
        disk_title.get_style_context().add_class("card-title")
        disk_card.pack_start(disk_title, False, False, 0)

        # Dropdown Combo
        combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        combo_label = Gtk.Label(label="Target Disk:")
        combo_label.set_xalign(0)
        combo_box.pack_start(combo_label, False, False, 0)

        self.disk_combo = Gtk.ComboBoxText()
        self.disk_combo.connect("changed", self.on_disk_selected)
        combo_box.pack_start(self.disk_combo, True, True, 0)
        disk_card.pack_start(combo_box, False, False, 0)

        # Partition Breakdown Frame
        self.part_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        disk_card.pack_start(self.part_box, False, False, 0)

        main_box.pack_start(disk_card, False, False, 0)

        # Card 2: Safety & Mount Status
        self.safety_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.safety_card.get_style_context().add_class("card")

        safety_title = Gtk.Label(label="🛡️ Safety & Data Protection Guard")
        safety_title.set_xalign(0)
        safety_title.get_style_context().add_class("card-title")
        self.safety_card.pack_start(safety_title, False, False, 0)

        # Status Indicators Grid
        self.safety_status_label = Gtk.Label(label="Checking safety...")
        self.safety_status_label.set_xalign(0)
        self.safety_status_label.set_line_wrap(True)
        self.safety_card.pack_start(self.safety_status_label, False, False, 0)

        # Safe Unmount & NTFS Repair Button Box
        self.unmount_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.unmount_btn = Gtk.Button(label="🔓 Safe Unmount Linux Partitions")
        self.unmount_btn.get_style_context().add_class("btn-warning")
        self.unmount_btn.connect("clicked", self.on_unmount_clicked)
        self.unmount_btn_box.pack_start(self.unmount_btn, False, False, 0)

        self.fix_ntfs_btn = Gtk.Button(label="⚡ Reset Status NTFS / Fast Startup")
        self.fix_ntfs_btn.get_style_context().add_class("btn-warning")
        self.fix_ntfs_btn.connect("clicked", self.on_fix_ntfs_clicked)
        self.unmount_btn_box.pack_start(self.fix_ntfs_btn, False, False, 0)

        self.safety_card.pack_start(self.unmount_btn_box, False, False, 0)

        main_box.pack_start(self.safety_card, False, False, 0)

        # Card 3: VM Resource Allocation Configuration
        config_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        config_card.get_style_context().add_class("card")

        config_title = Gtk.Label(label="⚙️ Virtual Machine Resource Settings")
        config_title.set_xalign(0)
        config_title.get_style_context().add_class("card-title")
        config_card.pack_start(config_title, False, False, 0)

        # Grid for sliders & options
        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(12)

        # Dynamic hardware recommendation calculation
        try:
            with open("/proc/meminfo", "r") as f:
                total_kb = int([line.split()[1] for line in f if "MemTotal" in line][0])
            total_ram_mb = total_kb // 1024
        except Exception:
            total_ram_mb = 8192

        if total_ram_mb <= 4096:
            rec_ram_mb = 2048
        elif total_ram_mb <= 8192:
            rec_ram_mb = 3072
        elif total_ram_mb <= 16384:
            rec_ram_mb = 6144
        else:
            rec_ram_mb = 8192

        max_cores = multiprocessing.cpu_count()
        if max_cores <= 2:
            rec_cores = 1
        elif max_cores <= 4:
            rec_cores = 2
        elif max_cores <= 8:
            rec_cores = 4
        else:
            rec_cores = max_cores // 2

        # RAM Slider with Recommended Mark Placeholder
        ram_lbl = Gtk.Label(label="RAM Allocation:")
        ram_lbl.set_xalign(0)
        grid.attach(ram_lbl, 0, 0, 1, 1)

        max_slider_ram = max(rec_ram_mb, min(16384, (total_ram_mb // 1024) * 1024))
        self.ram_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1024, max_slider_ram, 1024)
        self.ram_scale.set_value(rec_ram_mb)
        self.ram_scale.set_digits(0)
        self.ram_scale.set_hexpand(True)
        self.ram_scale.set_draw_value(True)
        self.ram_scale.add_mark(rec_ram_mb, Gtk.PositionType.BOTTOM, f"⭐ Rec ({int(rec_ram_mb/1024)} GB)")
        self.ram_scale.connect("format-value", lambda scale, val: f"{int(val/1024)} GB ({int(val)} MB)" + (" ⭐ Recommended" if int(val) == rec_ram_mb else ""))
        grid.attach(self.ram_scale, 1, 0, 1, 1)

        # CPU Cores Slider with Recommended Mark Placeholder
        cpu_lbl = Gtk.Label(label="CPU Cores:")
        cpu_lbl.set_xalign(0)
        grid.attach(cpu_lbl, 0, 1, 1, 1)

        self.cpu_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, max_cores, 1)
        self.cpu_scale.set_value(rec_cores)
        self.cpu_scale.set_digits(0)
        self.cpu_scale.set_hexpand(True)
        self.cpu_scale.set_draw_value(True)
        self.cpu_scale.add_mark(rec_cores, Gtk.PositionType.BOTTOM, f"⭐ Rec ({rec_cores} Cores)")
        self.cpu_scale.connect("format-value", lambda scale, val: f"{int(val)} Core" + ("s" if int(val) > 1 else "") + (" ⭐ Recommended" if int(val) == rec_cores else ""))
        grid.attach(self.cpu_scale, 1, 1, 1, 1)

        # Display Backend
        grid.attach(Gtk.Label(label="Display Engine:"), 0, 2, 1, 1)
        self.display_combo = Gtk.ComboBoxText()
        self.display_combo.append("gtk", "Native GTK Window (QXL 2D/3D)")
        self.display_combo.append("sdl", "SDL Hardware Window")
        self.display_combo.append("spice", "SPICE Protocol (Remote/Local)")
        self.display_combo.set_active(0)
        grid.attach(self.display_combo, 1, 2, 1, 1)

        # Fullscreen Toggle Checkbox
        self.fullscreen_chk = Gtk.CheckButton(label="🖥️ Jalankan VM Langsung dalam Mode Layar Penuh (Fullscreen)")
        grid.attach(self.fullscreen_chk, 0, 3, 2, 1)

        config_card.pack_start(grid, False, False, 0)
        main_box.pack_start(config_card, False, False, 0)

        # Card 4: VM Keyboard Shortcuts & Features Guide
        shortcut_expander = Gtk.Expander(label="⌨️ Fitur Canggih & Shortcut Layar VM (Fullscreen, Mouse, Keys)")
        shortcut_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        shortcut_card.get_style_context().add_class("card")

        shortcut_text = Gtk.Label()
        shortcut_text.set_xalign(0)
        shortcut_text.set_line_wrap(True)
        shortcut_text.set_markup(
            "<b>Daftar Fitur & Shortcut QEMU VM yang Bisa Kamu Gunakan:</b>\n\n"
            "• 🖥️ <b>Toggle Fullscreen:</b> Tekan <b><tt>Ctrl + Alt + F</tt></b> di dalam jendela VM untuk masuk/keluar mode Fullscreen kapan saja.\n"
            "• 🖱️ <b>Lepas / Tangkap Mouse:</b> Tekan <b><tt>Ctrl + Alt + G</tt></b> jika kursor kaku atau ingin melepas kursor dari VM.\n"
            "• 📐 <b>Layar Auto-Fit:</b> Di bar atas jendela VM, klik <b><i>View → Zoom to Fit</i></b> agar tampilan Windows pas secara otomatis dengan resolusi layar.\n"
            "• ⌨️ <b>Kirim Ctrl+Alt+Del:</b> Di bar atas jendela VM, klik <b><i>Machine → Send Key → Ctrl-Alt-Del</i></b> untuk membuka Task Manager / Lock Screen.\n"
            "• 🔄 <b>Hard Reset VM:</b> Di bar atas jendela VM, klik <b><i>Machine → Reset</i></b> jika Windows macet."
        )
        shortcut_card.pack_start(shortcut_text, False, False, 0)
        shortcut_expander.add(shortcut_card)
        main_box.pack_start(shortcut_expander, False, False, 0)

        # Card 4: Troubleshooting & Boot Help Guide
        help_expander = Gtk.Expander(label="💡 Windows Boot Troubleshooting & Fix Guide")
        help_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        help_card.get_style_context().add_class("card")

        help_text = Gtk.Label()
        help_text.set_xalign(0)
        help_text.set_line_wrap(True)
        help_text.set_markup(
            "<b>Jika Windows stuck di 'Preparing Automatic Repair':</b>\n\n"
            "1. <b>Matikan Fast Startup / Hibernasi di Windows:</b>\n"
            "   Di OS Windows fisik, buka CMD (Run as Administrator) dan ketik:\n"
            "   <tt>powercfg /h off</tt>\n"
            "   Lalu matikan Windows secara penuh (Shutdown, bukan Sleep/Hibernate).\n\n"
            "2. <b>Reset Status NTFS:</b> Klik tombol <i>'Reset Status NTFS'</i> di bagian Guard di atas untuk membersihkan dirty flag.\n\n"
            "3. <b>Boot ke Safe Mode sekali:</b>\n"
            "   Di layar Automatic Repair VM -> <i>Advanced Options</i> -> <i>Troubleshoot</i> -> <i>Startup Settings</i> -> <i>Restart</i> -> Tekan <b>4</b> (Enable Safe Mode).\n"
            "   Saat Safe Mode terbuka, Windows akan menyesuaikan driver virtual QEMU secara otomatis!"
        )
        help_card.pack_start(help_text, False, False, 0)
        help_expander.add(help_card)
        main_box.pack_start(help_expander, False, False, 0)

        # Smooth Loading State Progress Bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text("Ready to launch Windows VM")
        main_box.pack_start(self.progress_bar, False, False, 0)

        # Controls & Launch Bar
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.start_btn = Gtk.Button(label="▶ START WINDOWS VM")
        self.start_btn.get_style_context().add_class("btn-primary")
        self.start_btn.connect("clicked", self.on_start_vm_clicked)
        controls_box.pack_start(self.start_btn, True, True, 0)

        self.stop_btn = Gtk.Button(label="⏹ STOP VM")
        self.stop_btn.get_style_context().add_class("btn-danger")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self.on_stop_vm_clicked)
        controls_box.pack_start(self.stop_btn, False, False, 0)

        main_box.pack_start(controls_box, False, False, 0)

        # Console Logs Expander
        expander = Gtk.Expander(label="📄 Live Diagnostics & QEMU Console Output")
        log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(120)
        scrolled.set_hexpand(True)

        self.log_text_view = Gtk.TextView()
        self.log_text_view.set_editable(False)
        self.log_text_view.get_style_context().add_class("log-view")
        self.log_buffer = self.log_text_view.get_buffer()

        scrolled.add(self.log_text_view)
        log_box.pack_start(scrolled, True, True, 0)
        expander.add(log_box)

        main_box.pack_start(expander, False, False, 0)

    def update_kvm_badge(self):
        if self.deps.get("kvm_available"):
            self.kvm_badge.set_markup("<span foreground='#3fb950'><b>KVM: ENABLED 🚀</b></span>")
        else:
            self.kvm_badge.set_markup("<span foreground='#d29922'><b>KVM: NO ACCEL</b></span>")

    def update_dependency_ui(self):
        missing = self.deps.get("missing_packages", [])
        if missing:
            cmd_escaped = self.deps.get('install_command', '').replace('&', '&amp;')
            msg = f"Aplikasi membutuhkan komponen QEMU &amp; UEFI Firmware untuk menjalankan Windows VM.\n" \
                  f"Paket yang belum terpasang: <b>{', '.join(missing)}</b>\n\n" \
                  f"Silakan jalankan perintah berikut di Terminal:\n" \
                  f"<tt>{cmd_escaped}</tt>"
            self.dep_msg_label.set_markup(msg)
            self.dep_card.show_all()
        else:
            self.dep_card.hide()

    def copy_install_command(self, widget):
        cmd = self.deps.get('install_command', '')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(cmd, -1)
        self.log_message(f"Copied install command to clipboard: {cmd}")

    def refresh_disks(self):
        self.log_message("Scanning system dependencies and physical disks...")
        self.deps = SafetyChecker.check_system_dependencies()
        self.update_kvm_badge()
        self.update_dependency_ui()

        self.disks = DiskManager.get_physical_disks()
        self.disk_combo.remove_all()

        windows_index = -1
        for idx, disk in enumerate(self.disks):
            label = f"{disk['path']} — {disk['model']} ({disk['size_str']})"
            if disk.get("has_windows"):
                label += " [Windows Installed 🪟]"
                if windows_index == -1:
                    windows_index = idx
            self.disk_combo.append_text(label)

        if len(self.disks) > 0:
            active_idx = windows_index if windows_index != -1 else 0
            self.disk_combo.set_active(active_idx)
        else:
            self.log_message("Warning: No physical storage disks found.")

    def on_disk_selected(self, combo):
        idx = combo.get_active()
        if idx < 0 or idx >= len(self.disks):
            self.selected_disk = None
            return

        self.selected_disk = self.disks[idx]
        self.update_disk_details()

    def update_disk_details(self):
        if not self.selected_disk:
            return

        # Clear old partition widgets
        for child in self.part_box.get_children():
            self.part_box.remove(child)

        # Render Partition Breakdown
        parts_header = Gtk.Label(label=f"<b>Partition Layout for {self.selected_disk['path']}:</b>")
        parts_header.set_use_markup(True)
        parts_header.set_xalign(0)
        self.part_box.pack_start(parts_header, False, False, 4)

        for p in self.selected_disk.get("partitions", []):
            p_text = f"  • <b>{p['path']}</b> ({p['fstype'].upper() if p['fstype'] else 'Raw'}, {p['size_str']})"
            if p.get("label"):
                p_text += f" Label: <i>'{p['label']}'</i>"
            if p.get("is_mounted"):
                p_text += f" <span foreground='#dc2626'>[MOUNTED: {p['mountpoint']}]</span>"

            p_lbl = Gtk.Label()
            p_lbl.set_markup(p_text)
            p_lbl.set_xalign(0)
            self.part_box.pack_start(p_lbl, False, False, 1)

        self.part_box.show_all()

        # Run Safety Evaluation
        safety = SafetyChecker.check_disk_safety(self.selected_disk)
        self.eval_safety_ui(safety)

    def eval_safety_ui(self, safety):
        msg_lines = []
        is_safe = safety["is_safe"]

        if safety["unmount_required"]:
            msg_lines.append("<span foreground='#dc2626'><b>⚠️ MOUNT PROTECTION ACTIVE:</b></span> Partisi Windows sedang di-mount oleh Linux.")
            msg_lines.append("Harap unmount terlebih dahulu untuk mencegah kerusakan file NTFS.")
            self.unmount_btn_box.show_all()
        else:
            msg_lines.append("<span foreground='#16a34a'><b>✅ MOUNT GUARD: UNMOUNTED</b></span> (Aman untuk Booting)")
            self.unmount_btn_box.show_all()

        if safety["is_host_disk"]:
            msg_lines.append("<span foreground='#0284c7'><b>🛡️ DUAL-BOOT ISOLATION:</b></span> Disk ini juga berisi OS Linux Host.")
            msg_lines.append("BootBridge mengamankan passthrough agar Windows VM berjalan terisolasi.")

        self.safety_status_label.set_markup("\n".join(msg_lines))

        # Enable/Disable Start Button
        can_start = is_safe and self.deps.get("qemu_installed") and not self.launcher.is_running
        self.start_btn.set_sensitive(can_start)

    def on_unmount_clicked(self, widget):
        if not self.selected_disk:
            return

        mounted = self.selected_disk.get("mounted_partitions", [])
        for p in mounted:
            # Skip host system root /
            if p["mountpoint"] in ["/", "/boot", "/home"]:
                continue
            
            self.log_message(f"Unmounting partition {p['path']}...")
            success, msg = SafetyChecker.safe_unmount_partition(p["path"])
            self.log_message(msg)

        # Refresh disk status
        GLib.timeout_add(1000, self.refresh_disks)

    def on_fix_ntfs_clicked(self, widget):
        if not self.selected_disk:
            return

        ntfs_parts = [p for p in self.selected_disk.get("partitions", []) if p.get("fstype") == "ntfs"]
        if not ntfs_parts:
            self.log_message("Tidak ditemukan partisi NTFS pada disk yang dipilih.")
            return

        for p in ntfs_parts:
            self.log_message(f"Fixing NTFS dirty flag for partition {p['path']}...")
            success, msg = SafetyChecker.fix_ntfs_dirty_flag(p["path"])
            self.log_message(msg)

    def on_start_vm_clicked(self, widget):
        if not self.selected_disk:
            return

        ram_mb = int(self.ram_scale.get_value())
        cpu_cores = int(self.cpu_scale.get_value() if hasattr(self, "cpu_scale") else self.cpu_spin.get_value())
        display = self.display_combo.get_active_id() or "gtk"

        fullscreen = self.fullscreen_chk.get_active()
        self.log_message(f"Initiating VM boot for physical disk {self.selected_disk['path']} (Fullscreen={fullscreen})...")
        success = self.launcher.start_vm(
            disk_path=self.selected_disk["path"],
            ram_mb=ram_mb,
            cpu_cores=cpu_cores,
            display_type=display,
            fullscreen=fullscreen
        )

        if success:
            self.start_btn.set_sensitive(False)
            self.stop_btn.set_sensitive(True)
            self.progress_bar.set_fraction(0.5)
            self.progress_bar.set_text("Booting Windows VM... Initializing KVM Hypervisor ⚡")

    def on_stop_vm_clicked(self, widget):
        self.launcher.stop_vm()

    def on_vm_status_changed(self, status):
        def update_ui():
            if status == "RUNNING":
                self.start_btn.set_sensitive(False)
                self.stop_btn.set_sensitive(True)
                self.progress_bar.set_fraction(1.0)
                self.progress_bar.set_text("Windows VM Active & Running 🟢")
            else:
                self.start_btn.set_sensitive(True)
                self.stop_btn.set_sensitive(False)
                self.progress_bar.set_fraction(0.0)
                self.progress_bar.set_text("Ready to launch Windows VM")
        GLib.idle_add(update_ui)

    def log_message(self, message):
        def append_log():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, f"{message}\n")
            # Scroll to end
            mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
            self.log_text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_log)

def main():
    app = BootBridgeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    # Apply initial dep card visibility
    app.update_dependency_ui()
    Gtk.main()

if __name__ == "__main__":
    main()
