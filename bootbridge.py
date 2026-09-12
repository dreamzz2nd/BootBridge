#!/usr/bin/env python3
"""
BootBridge - Lightweight & Safe Dual-Boot Physical Windows Launcher for Linux
"""

import os
import sys
import json
import multiprocessing
import subprocess

# Ensure core package is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from core.disk_manager import DiskManager
from core.safety_checker import SafetyChecker
from core.qemu_launcher import QEMULauncher

# Configuration Persistence
CONFIG_DIR = os.path.expanduser("~/.config/bootbridge")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"language": "id", "theme": "dark"}

def save_config(config):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"[BootBridge] Error saving config: {e}")

# i18n Translations Dictionary
TRANSLATIONS = {
    "id": {
        "nav_title": "NAVIGATION",
        "nav_dashboard": "Dashboard & Drive",
        "nav_safety": "Proteksi & Safety",
        "nav_hardware": "Konfigurasi Hardware",
        "nav_guides": "Panduan & Shortcut",
        "nav_diagnostics": "Konsol Diagnostik",
        "nav_settings": "Pengaturan & Tema",
        "app_subtitle": "Peluncur VM Dual-Boot Windows Fisik yang Aman & Ringan",
        "kvm_active": "KVM: AKTIF",
        "kvm_disabled": "KVM: NONAKTIF",
        "dep_title": "Komponen Sistem Belum Lengkap",
        "copy_cmd": "Salin Perintah Instalasi",
        "dep_msg": "Aplikasi membutuhkan komponen QEMU &amp; UEFI Firmware untuk menjalankan Windows VM.\nPaket yang belum terpasang: <b>{missing}</b>\n\nSilakan jalankan perintah berikut di Terminal:\n<tt>{cmd}</tt>",
        "disk_card_title": "Drive Penyimpanan Fisik (Dual-Boot Windows)",
        "target_disk": "Disk Target:",
        "win_installed": " [Windows Terdeteksi]",
        "safety_card_title": "Proteksi & Keamanan Data File System",
        "unmount_btn": "Unmount Partisi Linux dengan Aman",
        "fix_ntfs_btn": "Reset Status NTFS / Fast Startup",
        "mount_active_hdr": "PROTEKSI MOUNT AKTIF:",
        "mount_active_msg": "Partisi Windows sedang di-mount oleh Linux. Harap unmount terlebih dahulu untuk mencegah kerusakan file NTFS.",
        "mount_safe_hdr": "PROTEKSI MOUNT: UNMOUNTED",
        "mount_safe_msg": "(Aman untuk Booting)",
        "dualboot_iso_hdr": "ISOLASI DUAL-BOOT:",
        "dualboot_iso_msg": "Disk ini juga berisi OS Linux Host. BootBridge mengamankan passthrough agar Windows VM berjalan terisolasi.",
        "config_card_title": "Pengaturan Alokasi Resource Virtual Machine",
        "ram_alloc": "Alokasi RAM:",
        "cpu_cores": "Core CPU:",
        "display_engine": "Mesin Tampilan:",
        "fullscreen_chk": "Jalankan VM Langsung dalam Mode Layar Penuh (Fullscreen)",
        "recommended": "Rekomendasi",
        "shortcut_title": "Fitur Canggih & Shortcut Layar VM (Fullscreen, Mouse, Keys)",
        "shortcut_markup": (
            "<b>Daftar Fitur &amp; Shortcut QEMU VM yang Bisa Kamu Gunakan:</b>\n\n"
            "• <b>Toggle Fullscreen:</b> Tekan <b><tt>Ctrl + Alt + F</tt></b> di dalam jendela VM untuk masuk/keluar mode Fullscreen kapan saja.\n"
            "• <b>Lepas / Tangkap Mouse:</b> Tekan <b><tt>Ctrl + Alt + G</tt></b> jika kursor kaku atau ingin melepas kursor dari VM.\n"
            "• <b>Layar Auto-Fit:</b> Di bar atas jendela VM, klik <b><i>View → Zoom to Fit</i></b> agar tampilan Windows pas secara otomatis dengan resolusi layar.\n"
            "• <b>Kirim Ctrl+Alt+Del:</b> Di bar atas jendela VM, klik <b><i>Machine → Send Key → Ctrl-Alt-Del</i></b> untuk membuka Task Manager / Lock Screen.\n"
            "• <b>Hard Reset VM:</b> Di bar atas jendela VM, klik <b><i>Machine → Reset</i></b> jika Windows macet."
        ),
        "help_title": "Panduan Troubleshooting Boot Windows",
        "help_markup": (
            "<b>Jika Windows stuck di 'Preparing Automatic Repair':</b>\n\n"
            "1. <b>Matikan Fast Startup / Hibernasi di Windows:</b>\n"
            "   Di OS Windows fisik, buka CMD (Run as Administrator) dan ketik:\n"
            "   <tt>powercfg /h off</tt>\n"
            "   Lalu matikan Windows secara penuh (Shutdown, bukan Sleep/Hibernate).\n\n"
            "2. <b>Reset Status NTFS:</b> Klik tombol <i>'Reset Status NTFS'</i> di bagian Guard di atas untuk membersihkan dirty flag.\n\n"
            "3. <b>Boot ke Safe Mode sekali:</b>\n"
            "   Di layar Automatic Repair VM -> <i>Advanced Options</i> -> <i>Troubleshoot</i> -> <i>Startup Settings</i> -> <i>Restart</i> -> Tekan <b>4</b> (Enable Safe Mode).\n"
            "   Saat Safe Mode terbuka, Windows akan menyesuaikan driver virtual QEMU secara otomatis!"
        ),
        "settings_card_title": "Tampilan & Preferensi Aplikasi",
        "theme_setting": "Mode Tema UI:",
        "theme_dark": "Mode Gelap (Postman Studio Dark)",
        "theme_light": "Mode Terang (Postman Studio Light)",
        "lang_setting": "Bahasa Aplikasi:",
        "sys_info_title": "Spesifikasi & Info Hypervisor Host",
        "progress_ready": "Siap menjalankan Windows VM",
        "progress_booting": "Memulai Windows VM... Mengaktifkan Hypervisor KVM",
        "progress_running": "Windows VM Berjalan & Aktif",
        "start_btn": "MULAI WINDOWS VM",
        "stop_btn": "HENTIKAN VM",
        "log_title": "Output Log Konsol & Diagnostik Langsung",
        "menu_language": "Bahasa:",
        "menu_theme": "Tema:",
        "menu_about": "Tentang BootBridge",
        "about_comments": "Peluncur VM Windows fisik dual-boot yang aman dan ringan untuk Linux melalui passthrough QEMU/KVM.",
    },
    "en": {
        "nav_title": "NAVIGATION",
        "nav_dashboard": "Dashboard & Drive",
        "nav_safety": "Safety & Mounts",
        "nav_hardware": "Resource Config",
        "nav_guides": "Help & Shortcuts",
        "nav_diagnostics": "Live Diagnostics",
        "nav_settings": "Settings & Theme",
        "app_subtitle": "Safe & Lightweight Dual-Boot Physical Windows VM Launcher",
        "kvm_active": "KVM: ACCELERATED",
        "kvm_disabled": "KVM: DISABLED",
        "dep_title": "System Dependencies Missing",
        "copy_cmd": "Copy Install Command",
        "dep_msg": "The application requires QEMU &amp; UEFI Firmware components to run the Windows VM.\nMissing packages: <b>{missing}</b>\n\nPlease run the following command in Terminal:\n<tt>{cmd}</tt>",
        "disk_card_title": "Physical Storage Drive (Dual-Boot Windows)",
        "target_disk": "Target Disk:",
        "win_installed": " [Windows Installed]",
        "safety_card_title": "Safety & Data Protection Guard",
        "unmount_btn": "Safe Unmount Linux Partitions",
        "fix_ntfs_btn": "Reset NTFS Status / Fast Startup",
        "mount_active_hdr": "MOUNT PROTECTION ACTIVE:",
        "mount_active_msg": "Windows partitions are currently mounted by Linux. Please unmount them first to prevent NTFS file corruption.",
        "mount_safe_hdr": "MOUNT GUARD: UNMOUNTED",
        "mount_safe_msg": "(Safe to Boot)",
        "dualboot_iso_hdr": "DUAL-BOOT ISOLATION:",
        "dualboot_iso_msg": "This drive also contains the Host Linux OS. BootBridge secures passthrough so Windows VM runs in isolation.",
        "config_card_title": "Virtual Machine Resource Settings",
        "ram_alloc": "RAM Allocation:",
        "cpu_cores": "CPU Cores:",
        "display_engine": "Display Engine:",
        "fullscreen_chk": "Launch VM Directly in Fullscreen Mode",
        "recommended": "Recommended",
        "shortcut_title": "VM Features & Screen Shortcuts (Fullscreen, Mouse, Keys)",
        "shortcut_markup": (
            "<b>Available QEMU VM Features &amp; Shortcuts:</b>\n\n"
            "• <b>Toggle Fullscreen:</b> Press <b><tt>Ctrl + Alt + F</tt></b> inside VM window to toggle Fullscreen mode.\n"
            "• <b>Release / Grab Mouse:</b> Press <b><tt>Ctrl + Alt + G</tt></b> to ungrab/release mouse pointer from VM.\n"
            "• <b>Screen Auto-Fit:</b> On VM window menu, click <b><i>View → Zoom to Fit</i></b> to fit Windows resolution automatically.\n"
            "• <b>Send Ctrl+Alt+Del:</b> On VM window menu, click <b><i>Machine → Send Key → Ctrl-Alt-Del</i></b> to access Task Manager / Lock Screen.\n"
            "• <b>Hard Reset VM:</b> On VM window menu, click <b><i>Machine → Reset</i></b> if Windows hangs."
        ),
        "help_title": "Windows Boot Troubleshooting & Fix Guide",
        "help_markup": (
            "<b>If Windows is stuck at 'Preparing Automatic Repair':</b>\n\n"
            "1. <b>Disable Fast Startup / Hibernation in Windows:</b>\n"
            "   In physical Windows OS, open CMD (Run as Administrator) and run:\n"
            "   <tt>powercfg /h off</tt>\n"
            "   Then shut down Windows completely (Shutdown, not Sleep/Hibernate).\n\n"
            "2. <b>Reset NTFS Status:</b> Click <i>'Reset NTFS Status'</i> in Safety Guard section above to clear dirty flags.\n\n"
            "3. <b>Boot to Safe Mode once:</b>\n"
            "   In VM Automatic Repair screen -> <i>Advanced Options</i> -> <i>Troubleshoot</i> -> <i>Startup Settings</i> -> <i>Restart</i> -> Press <b>4</b> (Enable Safe Mode).\n"
            "   When Safe Mode opens, Windows will automatically adapt QEMU virtual drivers!"
        ),
        "settings_card_title": "Appearance & Application Preferences",
        "theme_setting": "UI Theme Mode:",
        "theme_dark": "Dark Mode (Postman Studio Dark)",
        "theme_light": "Light Mode (Postman Studio Light)",
        "lang_setting": "Application Language:",
        "sys_info_title": "Host System & Hypervisor Specifications",
        "progress_ready": "Ready to launch Windows VM",
        "progress_booting": "Booting Windows VM... Initializing KVM Hypervisor",
        "progress_running": "Windows VM Active & Running",
        "start_btn": "START WINDOWS VM",
        "stop_btn": "STOP VM",
        "log_title": "Live Diagnostics & QEMU Console Output",
        "menu_language": "Language:",
        "menu_theme": "Theme:",
        "menu_about": "About BootBridge",
        "about_comments": "Lightweight & safe dual-boot physical Windows launcher for Linux via QEMU/KVM passthrough.",
    }
}

def make_card_header(icon_name, title_text):
    """Creates a card header box with a GTK symbolic icon and title label."""
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=title_text)
    label.set_xalign(0)
    label.get_style_context().add_class("card-title")
    box.pack_start(icon, False, False, 0)
    box.pack_start(label, False, False, 0)
    return box, label

def make_icon_button(icon_name, label_text, style_class=None):
    """Creates a GTK Button containing a GTK symbolic icon and label."""
    btn = Gtk.Button()
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    box.set_halign(Gtk.Align.CENTER)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=label_text)
    box.pack_start(icon, False, False, 0)
    box.pack_start(label, False, False, 0)
    btn.add(box)
    if style_class:
        btn.get_style_context().add_class(style_class)
    return btn, label

def make_icon_card_title(icon_name, title_text):
    """Creates a card header box with a symbolic icon header."""
    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=title_text)
    label.get_style_context().add_class("card-title")
    header_box.pack_start(icon, False, False, 0)
    header_box.pack_start(label, False, False, 0)
    return header_box, label


class BootBridgeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="BootBridge")
        self.set_default_size(880, 680)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Set Window Icon
        icon_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
        if os.path.exists(icon_path):
            try:
                self.set_icon_from_file(icon_path)
            except Exception as e:
                print(f"[BootBridge] Warning setting window icon: {e}")

        # Load Saved Config & Preferences
        self.config = load_config()
        self.current_lang = self.config.get("language", "id")
        self.current_theme = self.config.get("theme", "dark")
        self.css_provider = None

        # State Variables
        self.disks = []
        self.selected_disk = None
        self.deps = SafetyChecker.check_system_dependencies()
        self.launcher = QEMULauncher(log_callback=self.log_message, status_callback=self.on_vm_status_changed)

        # Load Custom CSS Styling (Dark or Light)
        self.load_css()

        # Build GUI Layout
        self.build_ui()

        # Refresh disk listing & apply language
        self.apply_language()

    def tr(self, key, **kwargs):
        lang = self.current_lang if self.current_lang in TRANSLATIONS else "id"
        text = TRANSLATIONS[lang].get(key, TRANSLATIONS["id"].get(key, key))
        if kwargs:
            text = text.format(**kwargs)
        return text

    def load_css(self):
        theme = self.config.get("theme", "dark")
        css_filename = "style_dark.css" if theme == "dark" else "style_light.css"
        css_path = os.path.join(BASE_DIR, "assets", css_filename)

        if self.css_provider:
            try:
                Gtk.StyleContext.remove_provider_for_screen(
                    Gdk.Screen.get_default(),
                    self.css_provider
                )
            except Exception:
                pass
        
        self.css_provider = Gtk.CssProvider()
        if os.path.exists(css_path):
            try:
                self.css_provider.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    self.css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"[BootBridge] Warning loading CSS ({css_filename}): {e}")

    def build_ui(self):
        # HeaderBar
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "BootBridge"
        self.header.props.subtitle = self.tr("app_subtitle")
        self.set_titlebar(self.header)

        # Refresh Button
        refresh_btn = Gtk.Button()
        refresh_btn.set_tooltip_text("Refresh Physical Disks")
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_btn.add(refresh_icon)
        refresh_btn.connect("clicked", lambda x: self.refresh_disks())
        self.header.pack_start(refresh_btn)

        # Main Horizontal Window Box (Sidebar + Main Content Area)
        main_h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(main_h_box)

        # ==========================================
        # LEFT NAVIGATION SIDEBAR
        # ==========================================
        sidebar_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar_container.get_style_context().add_class("sidebar")

        self.sidebar_title_lbl = Gtk.Label(label=self.tr("nav_title"))
        self.sidebar_title_lbl.set_xalign(0)
        self.sidebar_title_lbl.get_style_context().add_class("sidebar-title")
        sidebar_container.pack_start(self.sidebar_title_lbl, False, False, 4)

        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.get_style_context().add_class("sidebar-list")
        self.sidebar_list.connect("row-selected", self.on_sidebar_row_selected)

        self.nav_items = [
            ("dashboard", "drive-harddisk-symbolic", "nav_dashboard"),
            ("safety", "security-high-symbolic", "nav_safety"),
            ("hardware", "preferences-system-symbolic", "nav_hardware"),
            ("guides", "input-keyboard-symbolic", "nav_guides"),
            ("diagnostics", "utilities-terminal-symbolic", "nav_diagnostics"),
            ("settings", "emblem-system-symbolic", "nav_settings")
        ]

        self.nav_labels = {}
        for page_id, icon_name, tr_key in self.nav_items:
            row = Gtk.ListBoxRow()
            row.page_id = page_id
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.get_style_context().add_class("sidebar-row")
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            lbl = Gtk.Label(label=self.tr(tr_key))
            lbl.set_xalign(0)
            box.pack_start(icon, False, False, 0)
            box.pack_start(lbl, True, True, 0)
            row.add(box)
            self.sidebar_list.add(row)
            self.nav_labels[page_id] = lbl

        sidebar_container.pack_start(self.sidebar_list, True, True, 0)
        main_h_box.pack_start(sidebar_container, False, False, 0)

        # ==========================================
        # RIGHT CONTENT PANEL (STACK + BOTTOM BAR)
        # ==========================================
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_h_box.pack_start(right_panel, True, True, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        right_panel.pack_start(self.stack, True, True, 0)

        # ------------------------------------------
        # Page 1: Dashboard & Physical Storage Drive
        # ------------------------------------------
        page_dash_scroll = Gtk.ScrolledWindow()
        page_dash_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_dash_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_dash_box.set_margin_top(16)
        page_dash_box.set_margin_bottom(16)
        page_dash_box.set_margin_start(16)
        page_dash_box.set_margin_end(16)
        page_dash_scroll.add(page_dash_box)

        # Dependency Warning Card
        self.dep_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.dep_card.get_style_context().add_class("card")
        self.dep_card.get_style_context().add_class("badge-warning")
        
        dep_title_box, self.dep_title_lbl = make_card_header("dialog-warning-symbolic", self.tr("dep_title"))
        self.dep_card.pack_start(dep_title_box, False, False, 0)

        self.dep_msg_label = Gtk.Label()
        self.dep_msg_label.set_xalign(0)
        self.dep_msg_label.set_line_wrap(True)
        self.dep_card.pack_start(self.dep_msg_label, False, False, 0)

        dep_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.copy_cmd_btn, self.copy_cmd_btn_lbl = make_icon_button("edit-copy-symbolic", self.tr("copy_cmd"))
        self.copy_cmd_btn.connect("clicked", self.copy_install_command)
        dep_btn_box.pack_start(self.copy_cmd_btn, False, False, 0)
        self.dep_card.pack_start(dep_btn_box, False, False, 0)
        page_dash_box.pack_start(self.dep_card, False, False, 0)
        self.update_dependency_ui()

        # Disk Card
        disk_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        disk_card.get_style_context().add_class("card")

        disk_title_box, self.disk_title_lbl = make_card_header("drive-harddisk-symbolic", self.tr("disk_card_title"))
        disk_card.pack_start(disk_title_box, False, False, 0)

        combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.combo_label = Gtk.Label(label=self.tr("target_disk"))
        self.combo_label.set_xalign(0)
        combo_box.pack_start(self.combo_label, False, False, 0)

        self.disk_combo = Gtk.ComboBoxText()
        self.disk_combo.connect("changed", self.on_disk_selected)
        combo_box.pack_start(self.disk_combo, True, True, 0)
        disk_card.pack_start(combo_box, False, False, 0)

        self.part_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        disk_card.pack_start(self.part_box, False, False, 0)
        page_dash_box.pack_start(disk_card, False, False, 0)

        self.stack.add_named(page_dash_scroll, "dashboard")

        # ------------------------------------------
        # Page 2: Safety & Data Protection Guard
        # ------------------------------------------
        page_safety_scroll = Gtk.ScrolledWindow()
        page_safety_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_safety_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_safety_box.set_margin_top(16)
        page_safety_box.set_margin_bottom(16)
        page_safety_box.set_margin_start(16)
        page_safety_box.set_margin_end(16)
        page_safety_scroll.add(page_safety_box)

        self.safety_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.safety_card.get_style_context().add_class("card")

        safety_title_box, self.safety_title_lbl = make_card_header("security-high-symbolic", self.tr("safety_card_title"))
        self.safety_card.pack_start(safety_title_box, False, False, 0)

        self.safety_status_label = Gtk.Label(label="Checking safety...")
        self.safety_status_label.set_xalign(0)
        self.safety_status_label.set_line_wrap(True)
        self.safety_card.pack_start(self.safety_status_label, False, False, 0)

        self.unmount_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.unmount_btn, self.unmount_btn_lbl = make_icon_button("drive-removable-media-symbolic", self.tr("unmount_btn"), style_class="btn-warning")
        self.unmount_btn.connect("clicked", self.on_unmount_clicked)
        self.unmount_btn_box.pack_start(self.unmount_btn, False, False, 0)

        self.fix_ntfs_btn, self.fix_ntfs_btn_lbl = make_icon_button("system-run-symbolic", self.tr("fix_ntfs_btn"), style_class="btn-warning")
        self.fix_ntfs_btn.connect("clicked", self.on_fix_ntfs_clicked)
        self.unmount_btn_box.pack_start(self.fix_ntfs_btn, False, False, 0)
        self.safety_card.pack_start(self.unmount_btn_box, False, False, 0)

        page_safety_box.pack_start(self.safety_card, False, False, 0)
        self.stack.add_named(page_safety_scroll, "safety")

        # ------------------------------------------
        # Page 3: Hardware Resource Config
        # ------------------------------------------
        page_hw_scroll = Gtk.ScrolledWindow()
        page_hw_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_hw_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_hw_box.set_margin_top(16)
        page_hw_box.set_margin_bottom(16)
        page_hw_box.set_margin_start(16)
        page_hw_box.set_margin_end(16)
        page_hw_scroll.add(page_hw_box)

        config_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        config_card.get_style_context().add_class("card")

        config_title_box, self.config_title_lbl = make_card_header("preferences-system-symbolic", self.tr("config_card_title"))
        config_card.pack_start(config_title_box, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(14)

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

        self.rec_ram_mb = rec_ram_mb
        self.rec_cores = rec_cores

        self.ram_lbl = Gtk.Label(label=self.tr("ram_alloc"))
        self.ram_lbl.set_xalign(0)
        grid.attach(self.ram_lbl, 0, 0, 1, 1)

        max_slider_ram = max(rec_ram_mb, min(16384, (total_ram_mb // 1024) * 1024))
        self.ram_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1024, max_slider_ram, 1024)
        self.ram_scale.set_value(rec_ram_mb)
        self.ram_scale.set_digits(0)
        self.ram_scale.set_hexpand(True)
        self.ram_scale.set_draw_value(True)
        grid.attach(self.ram_scale, 1, 0, 1, 1)

        self.cpu_lbl = Gtk.Label(label=self.tr("cpu_cores"))
        self.cpu_lbl.set_xalign(0)
        grid.attach(self.cpu_lbl, 0, 1, 1, 1)

        self.cpu_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, max_cores, 1)
        self.cpu_scale.set_value(rec_cores)
        self.cpu_scale.set_digits(0)
        self.cpu_scale.set_hexpand(True)
        self.cpu_scale.set_draw_value(True)
        grid.attach(self.cpu_scale, 1, 1, 1, 1)

        self.update_scale_marks()

        self.display_lbl = Gtk.Label(label=self.tr("display_engine"))
        self.display_lbl.set_xalign(0)
        grid.attach(self.display_lbl, 0, 2, 1, 1)

        self.display_combo = Gtk.ComboBoxText()
        self.display_combo.append("gtk", "Native GTK Window (QXL 2D/3D)")
        self.display_combo.append("sdl", "SDL Hardware Window")
        self.display_combo.append("spice", "SPICE Protocol (Remote/Local)")
        self.display_combo.set_active(0)
        grid.attach(self.display_combo, 1, 2, 1, 1)

        self.fullscreen_chk = Gtk.CheckButton(label=self.tr("fullscreen_chk"))
        grid.attach(self.fullscreen_chk, 0, 3, 2, 1)

        config_card.pack_start(grid, False, False, 0)
        page_hw_box.pack_start(config_card, False, False, 0)
        self.stack.add_named(page_hw_scroll, "hardware")

        # ------------------------------------------
        # Page 4: Guides & Shortcuts
        # ------------------------------------------
        page_guides_scroll = Gtk.ScrolledWindow()
        page_guides_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_guides_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_guides_box.set_margin_top(16)
        page_guides_box.set_margin_bottom(16)
        page_guides_box.set_margin_start(16)
        page_guides_box.set_margin_end(16)
        page_guides_scroll.add(page_guides_box)

        # Shortcuts Card
        shortcut_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        shortcut_card.get_style_context().add_class("card")

        shortcut_header, self.shortcut_title_lbl = make_icon_card_title("input-keyboard-symbolic", self.tr("shortcut_title"))
        shortcut_card.pack_start(shortcut_header, False, False, 0)

        self.shortcut_text = Gtk.Label()
        self.shortcut_text.set_xalign(0)
        self.shortcut_text.set_line_wrap(True)
        self.shortcut_text.set_markup(self.tr("shortcut_markup"))
        shortcut_card.pack_start(self.shortcut_text, False, False, 0)
        page_guides_box.pack_start(shortcut_card, False, False, 0)

        # Troubleshooting Card
        help_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        help_card.get_style_context().add_class("card")

        help_header, self.help_title_lbl = make_icon_card_title("help-faq-symbolic", self.tr("help_title"))
        help_card.pack_start(help_header, False, False, 0)

        self.help_text = Gtk.Label()
        self.help_text.set_xalign(0)
        self.help_text.set_line_wrap(True)
        self.help_text.set_markup(self.tr("help_markup"))
        help_card.pack_start(self.help_text, False, False, 0)
        page_guides_box.pack_start(help_card, False, False, 0)

        self.stack.add_named(page_guides_scroll, "guides")

        # ------------------------------------------
        # Page 5: Live Diagnostics Console Output
        # ------------------------------------------
        page_log_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        page_log_box.set_margin_top(16)
        page_log_box.set_margin_bottom(16)
        page_log_box.set_margin_start(16)
        page_log_box.set_margin_end(16)

        log_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        log_card.get_style_context().add_class("card")

        log_header, self.log_title_lbl = make_icon_card_title("utilities-terminal-symbolic", self.tr("log_title"))
        log_card.pack_start(log_header, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(350)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        self.log_text_view = Gtk.TextView()
        self.log_text_view.set_editable(False)
        self.log_text_view.get_style_context().add_class("log-view")
        self.log_buffer = self.log_text_view.get_buffer()

        scrolled.add(self.log_text_view)
        log_card.pack_start(scrolled, True, True, 0)
        page_log_box.pack_start(log_card, True, True, 0)

        self.stack.add_named(page_log_box, "diagnostics")

        # ------------------------------------------
        # Page 6: Dedicated Settings Page (Theme & Language)
        # ------------------------------------------
        page_sett_scroll = Gtk.ScrolledWindow()
        page_sett_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        page_sett_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_sett_box.set_margin_top(16)
        page_sett_box.set_margin_bottom(16)
        page_sett_box.set_margin_start(16)
        page_sett_box.set_margin_end(16)
        page_sett_scroll.add(page_sett_box)

        # Settings Card 1: Appearance & Language
        sett_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        sett_card.get_style_context().add_class("card")

        sett_title_box, self.sett_title_lbl = make_card_header("emblem-system-symbolic", self.tr("settings_card_title"))
        sett_card.pack_start(sett_title_box, False, False, 0)

        sett_grid = Gtk.Grid()
        sett_grid.set_column_spacing(16)
        sett_grid.set_row_spacing(14)

        # Theme Selector
        self.sett_theme_lbl = Gtk.Label(label=self.tr("theme_setting"))
        self.sett_theme_lbl.set_xalign(0)
        sett_grid.attach(self.sett_theme_lbl, 0, 0, 1, 1)

        self.sett_theme_combo = Gtk.ComboBoxText()
        self.sett_theme_combo.append("dark", self.tr("theme_dark"))
        self.sett_theme_combo.append("light", self.tr("theme_light"))
        self.sett_theme_combo.set_active_id(self.current_theme)
        self.sett_theme_combo.connect("changed", self.on_theme_changed)
        sett_grid.attach(self.sett_theme_combo, 1, 0, 1, 1)

        # Language Selector
        self.sett_lang_lbl = Gtk.Label(label=self.tr("lang_setting"))
        self.sett_lang_lbl.set_xalign(0)
        sett_grid.attach(self.sett_lang_lbl, 0, 1, 1, 1)

        self.sett_lang_combo = Gtk.ComboBoxText()
        self.sett_lang_combo.append("id", "Bahasa Indonesia")
        self.sett_lang_combo.append("en", "English")
        self.sett_lang_combo.set_active_id(self.current_lang)
        self.sett_lang_combo.connect("changed", self.on_language_changed)
        sett_grid.attach(self.sett_lang_combo, 1, 1, 1, 1)

        sett_card.pack_start(sett_grid, False, False, 0)
        page_sett_box.pack_start(sett_card, False, False, 0)

        # Settings Card 2: System Hypervisor Specs
        sys_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sys_card.get_style_context().add_class("card")

        sys_title_box, self.sys_title_lbl = make_card_header("computer-symbolic", self.tr("sys_info_title"))
        sys_card.pack_start(sys_title_box, False, False, 0)

        sys_info_lbl = Gtk.Label()
        sys_info_lbl.set_xalign(0)
        sys_info_lbl.set_markup(
            f"• <b>Host Cores:</b> {multiprocessing.cpu_count()} CPU Threads\n"
            f"• <b>Memory RAM:</b> {int(total_ram_mb/1024)} GB Total\n"
            f"• <b>KVM Acceleration:</b> {'Supported &amp; Enabled' if self.deps.get('kvm_available') else 'Disabled / Unavailable'}\n"
            f"• <b>QEMU Package:</b> {'Installed' if self.deps.get('qemu_installed') else 'Missing'}\n"
            f"• <b>OVMF Firmware:</b> {'Installed' if self.deps.get('ovmf_installed') else 'Missing'}"
        )
        sys_card.pack_start(sys_info_lbl, False, False, 0)
        page_sett_box.pack_start(sys_card, False, False, 0)

        self.stack.add_named(page_sett_scroll, "settings")

        # Select first row in sidebar
        first_row = self.sidebar_list.get_row_at_index(0)
        if first_row:
            self.sidebar_list.select_row(first_row)

        # ==========================================
        # BOTTOM ACTION LAUNCHER BAR (PINNED ALWAYS)
        # ==========================================
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bottom_bar.get_style_context().add_class("bottom-bar")

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(True)
        self.progress_bar.set_text(self.tr("progress_ready"))
        bottom_bar.pack_start(self.progress_bar, False, False, 0)

        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.start_btn, self.start_btn_lbl = make_icon_button("media-playback-start-symbolic", self.tr("start_btn"), style_class="btn-primary")
        self.start_btn.connect("clicked", self.on_start_vm_clicked)
        controls_box.pack_start(self.start_btn, True, True, 0)

        self.stop_btn, self.stop_btn_lbl = make_icon_button("media-playback-stop-symbolic", self.tr("stop_btn"), style_class="btn-danger")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self.on_stop_vm_clicked)
        controls_box.pack_start(self.stop_btn, False, False, 0)

        bottom_bar.pack_start(controls_box, False, False, 0)
        right_panel.pack_start(bottom_bar, False, False, 0)

    def on_sidebar_row_selected(self, listbox, row):
        if row and hasattr(row, "page_id"):
            self.stack.set_visible_child_name(row.page_id)

    def update_scale_marks(self):
        rec_lbl = self.tr("recommended")
        self.ram_scale.clear_marks()
        self.ram_scale.add_mark(self.rec_ram_mb, Gtk.PositionType.BOTTOM, f"{rec_lbl} ({int(self.rec_ram_mb/1024)} GB)")
        self.ram_scale.connect("format-value", lambda scale, val: f"{int(val/1024)} GB ({int(val)} MB)" + (f" ({rec_lbl})" if int(val) == self.rec_ram_mb else ""))

        self.cpu_scale.clear_marks()
        self.cpu_scale.add_mark(self.rec_cores, Gtk.PositionType.BOTTOM, f"{rec_lbl} ({self.rec_cores} Cores)")
        self.cpu_scale.connect("format-value", lambda scale, val: f"{int(val)} Core" + ("s" if int(val) > 1 else "") + (f" ({rec_lbl})" if int(val) == self.rec_cores else ""))

    def on_theme_changed(self, combo):
        new_theme = combo.get_active_id()
        if new_theme and new_theme != self.current_theme:
            self.current_theme = new_theme
            self.config["theme"] = new_theme
            save_config(self.config)
            
            # Sync other combo if different
            if hasattr(self, "pop_theme_combo") and self.pop_theme_combo.get_active_id() != new_theme:
                self.pop_theme_combo.set_active_id(new_theme)
            if hasattr(self, "sett_theme_combo") and self.sett_theme_combo.get_active_id() != new_theme:
                self.sett_theme_combo.set_active_id(new_theme)

            self.load_css()

    def on_language_changed(self, combo):
        new_lang = combo.get_active_id()
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.config["language"] = new_lang
            save_config(self.config)

            # Sync other combo if different
            if hasattr(self, "pop_lang_combo") and self.pop_lang_combo.get_active_id() != new_lang:
                self.pop_lang_combo.set_active_id(new_lang)
            if hasattr(self, "sett_lang_combo") and self.sett_lang_combo.get_active_id() != new_lang:
                self.sett_lang_combo.set_active_id(new_lang)

            self.apply_language()

    def apply_language(self):
        if hasattr(self, "header"):
            self.header.props.subtitle = self.tr("app_subtitle")
        
        self.update_kvm_badge()
        self.update_dependency_ui()

        if hasattr(self, "sidebar_title_lbl"):
            self.sidebar_title_lbl.set_text(self.tr("nav_title"))

        for page_id, icon_name, tr_key in getattr(self, "nav_items", []):
            if page_id in self.nav_labels:
                self.nav_labels[page_id].set_text(self.tr(tr_key))

        if hasattr(self, "dep_title_lbl"): self.dep_title_lbl.set_text(self.tr("dep_title"))
        if hasattr(self, "copy_cmd_btn_lbl"): self.copy_cmd_btn_lbl.set_text(self.tr("copy_cmd"))
        if hasattr(self, "disk_title_lbl"): self.disk_title_lbl.set_text(self.tr("disk_card_title"))
        if hasattr(self, "combo_label"): self.combo_label.set_text(self.tr("target_disk"))
        if hasattr(self, "safety_title_lbl"): self.safety_title_lbl.set_text(self.tr("safety_card_title"))
        if hasattr(self, "unmount_btn_lbl"): self.unmount_btn_lbl.set_text(self.tr("unmount_btn"))
        if hasattr(self, "fix_ntfs_btn_lbl"): self.fix_ntfs_btn_lbl.set_text(self.tr("fix_ntfs_btn"))
        if hasattr(self, "config_title_lbl"): self.config_title_lbl.set_text(self.tr("config_card_title"))
        if hasattr(self, "ram_lbl"): self.ram_lbl.set_text(self.tr("ram_alloc"))
        if hasattr(self, "cpu_lbl"): self.cpu_lbl.set_text(self.tr("cpu_cores"))
        if hasattr(self, "display_lbl"): self.display_lbl.set_text(self.tr("display_engine"))
        if hasattr(self, "fullscreen_chk"): self.fullscreen_chk.set_label(self.tr("fullscreen_chk"))
        if hasattr(self, "shortcut_title_lbl"): self.shortcut_title_lbl.set_text(self.tr("shortcut_title"))
        if hasattr(self, "shortcut_text"): self.shortcut_text.set_markup(self.tr("shortcut_markup"))
        if hasattr(self, "help_title_lbl"): self.help_title_lbl.set_text(self.tr("help_title"))
        if hasattr(self, "help_text"): self.help_text.set_markup(self.tr("help_markup"))
        if hasattr(self, "log_title_lbl"): self.log_title_lbl.set_text(self.tr("log_title"))
        if hasattr(self, "sett_title_lbl"): self.sett_title_lbl.set_text(self.tr("settings_card_title"))
        if hasattr(self, "sett_theme_lbl"): self.sett_theme_lbl.set_text(self.tr("theme_setting"))
        if hasattr(self, "sett_lang_lbl"): self.sett_lang_lbl.set_text(self.tr("lang_setting"))
        if hasattr(self, "sys_title_lbl"): self.sys_title_lbl.set_text(self.tr("sys_info_title"))
        if hasattr(self, "start_btn_lbl"): self.start_btn_lbl.set_text(self.tr("start_btn"))
        if hasattr(self, "stop_btn_lbl"): self.stop_btn_lbl.set_text(self.tr("stop_btn"))
        if hasattr(self, "menu_lang_lbl"): self.menu_lang_lbl.set_text(self.tr("menu_language"))
        if hasattr(self, "menu_theme_lbl"): self.menu_theme_lbl.set_text(self.tr("menu_theme"))
        if hasattr(self, "about_btn_lbl"): self.about_btn_lbl.set_text(self.tr("menu_about"))

        if hasattr(self, "ram_scale"):
            self.update_scale_marks()

        if not self.launcher.is_running and hasattr(self, "progress_bar"):
            self.progress_bar.set_text(self.tr("progress_ready"))

        self.refresh_disks()

    def show_about_dialog(self, widget=None):
        dialog = Gtk.AboutDialog()
        dialog.set_transient_for(self)
        dialog.set_program_name("BootBridge")
        dialog.set_version("1.0.0")
        dialog.set_comments(self.tr("about_comments"))
        dialog.set_website("https://github.com/dreamzz2nd/BootBridge")
        dialog.set_website_label("GitHub Repository")
        dialog.set_authors(["BootBridge Development Team"])
        
        icon_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
        if os.path.exists(icon_path):
            try:
                pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(icon_path, 128, 128, True)
                dialog.set_logo(pixbuf)
            except Exception:
                dialog.set_logo_icon_name("drive-harddisk-symbolic")
        else:
            dialog.set_logo_icon_name("drive-harddisk-symbolic")

        dialog.set_copyright("Copyright © 2026 BootBridge Project")
        dialog.run()
        dialog.destroy()

    def update_kvm_badge(self):
        if hasattr(self, "kvm_badge") and self.kvm_badge:
            if self.deps.get("kvm_available"):
                self.kvm_badge.set_markup(f"<span foreground='#73c991'><b>{self.tr('kvm_active')}</b></span>")
            else:
                self.kvm_badge.set_markup(f"<span foreground='#ffb74d'><b>{self.tr('kvm_disabled')}</b></span>")

    def update_dependency_ui(self):
        missing = self.deps.get("missing_packages", [])
        if missing:
            cmd_escaped = self.deps.get('install_command', '').replace('&', '&amp;')
            msg = self.tr("dep_msg", missing=', '.join(missing), cmd=cmd_escaped)
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
        win_suffix = self.tr("win_installed")
        for idx, disk in enumerate(self.disks):
            label = f"{disk['path']} — {disk['model']} ({disk['size_str']})"
            if disk.get("has_windows"):
                label += win_suffix
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
                p_text += f" <span foreground='#ef5350'>[MOUNTED: {p['mountpoint']}]</span>"

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
            hdr = self.tr("mount_active_hdr")
            body = self.tr("mount_active_msg")
            msg_lines.append(f"<span foreground='#ef5350'><b>{hdr}</b></span> {body}")
            self.unmount_btn_box.show_all()
        else:
            hdr = self.tr("mount_safe_hdr")
            body = self.tr("mount_safe_msg")
            msg_lines.append(f"<span foreground='#73c991'><b>{hdr}</b></span> {body}")
            self.unmount_btn_box.show_all()

        if safety["is_host_disk"]:
            hdr = self.tr("dualboot_iso_hdr")
            body = self.tr("dualboot_iso_msg")
            msg_lines.append(f"<span foreground='#64b5f6'><b>{hdr}</b></span> {body}")

        self.safety_status_label.set_markup("\n".join(msg_lines))

        # Enable/Disable Start Button
        can_start = is_safe and self.deps.get("qemu_installed") and not self.launcher.is_running
        self.start_btn.set_sensitive(can_start)

    def on_unmount_clicked(self, widget):
        if not self.selected_disk:
            return

        mounted = self.selected_disk.get("mounted_partitions", [])
        for p in mounted:
            if p["mountpoint"] in ["/", "/boot", "/home"]:
                continue
            
            self.log_message(f"Unmounting partition {p['path']}...")
            success, msg = SafetyChecker.safe_unmount_partition(p["path"])
            self.log_message(msg)

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
        cpu_cores = int(self.cpu_scale.get_value())
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
            self.progress_bar.set_text(self.tr("progress_booting"))

    def on_stop_vm_clicked(self, widget):
        self.launcher.stop_vm()

    def on_vm_status_changed(self, status):
        def update_ui():
            if status == "RUNNING":
                self.start_btn.set_sensitive(False)
                self.stop_btn.set_sensitive(True)
                self.progress_bar.set_fraction(1.0)
                self.progress_bar.set_text(self.tr("progress_running"))
            else:
                self.start_btn.set_sensitive(True)
                self.stop_btn.set_sensitive(False)
                self.progress_bar.set_fraction(0.0)
                self.progress_bar.set_text(self.tr("progress_ready"))
        GLib.idle_add(update_ui)

    def log_message(self, message):
        def append_log():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, f"{message}\n")
            mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
            self.log_text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_log)

def main():
    app = BootBridgeApp()
    app.connect("destroy", Gtk.main_quit)
    app.show_all()
    app.update_dependency_ui()
    Gtk.main()

if __name__ == "__main__":
    main()
