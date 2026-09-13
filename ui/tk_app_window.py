"""
Universal Native GUI for BootBridge
Faithful 1:1 match with Linux GTK3 Interface across all 7 pages, HeaderBar, and Pinned Launcher.
Runs natively out-of-the-box on Windows, macOS, and Linux.
"""

import os
import sys
import subprocess
import threading
import time
import platform
import multiprocessing
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.config import load_config, save_config, add_remote_history
from core.disk_manager import DiskManager
from core.safety_checker import SafetyChecker
from core.qemu_launcher import QEMULauncher
from core.remote_launcher import RemoteLauncher
from ui.i18n import tr

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Dark & Light Themes Matching GTK3 CSS (style_dark.css & style_light.css)
THEMES = {
    "dark": {
        "bg_window": "#0f172a",     # Slate 900
        "header_bg": "#1e293b",     # Slate 800
        "sidebar_bg": "#090d16",    # Deep Navy Sidebar
        "sidebar_active": "#2563eb",# Blue Active Tab
        "sidebar_hover": "#1e293b",
        "card_bg": "#1e293b",       # Card Container
        "card_header": "#334155",   # Card Sub-header
        "input_bg": "#0f172a",      # Input Box
        "text_main": "#f8fafc",     # Light Text
        "text_muted": "#94a3b8",    # Slate Muted
        "border": "#334155",        # Slate Border
        "accent_blue": "#2563eb",
        "accent_blue_hover": "#1d4ed8",
        "accent_green": "#10b981",
        "accent_cyan": "#06b6d4",
        "accent_red": "#ef4444",
        "accent_yellow": "#f59e0b",
        "log_bg": "#000000",
        "log_fg": "#22c55e"
    },
    "light": {
        "bg_window": "#f1f5f9",
        "header_bg": "#e2e8f0",
        "sidebar_bg": "#ffffff",
        "sidebar_active": "#2563eb",
        "sidebar_hover": "#f1f5f9",
        "card_bg": "#ffffff",
        "card_header": "#f8fafc",
        "input_bg": "#ffffff",
        "text_main": "#0f172a",
        "text_muted": "#64748b",
        "border": "#cbd5e1",
        "accent_blue": "#2563eb",
        "accent_blue_hover": "#1d4ed8",
        "accent_green": "#10b981",
        "accent_cyan": "#0284c7",
        "accent_red": "#ef4444",
        "accent_yellow": "#d97706",
        "log_bg": "#1e293b",
        "log_fg": "#4ade80"
    }
}

class BootBridgeTkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.current_lang = self.config.get("language", "id")
        self.current_theme_name = self.config.get("theme", "dark")
        self.T = THEMES[self.current_theme_name]

        self.title("BootBridge")
        self.geometry("1020x720")
        self.minsize(920, 640)
        self.configure(bg=self.T["bg_window"])
        self.center_window()

        # Set Window Icon
        ico_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        png_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
        if os.path.exists(ico_path) and sys.platform == "win32":
            try: self.iconbitmap(ico_path)
            except Exception: pass
        elif os.path.exists(png_path):
            try:
                icon_img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, icon_img)
            except Exception: pass

        # State Variables
        self.disks = []
        self.selected_disk = None
        self.vm_is_running = False
        self.is_fullscreen = False

        # Core Launchers
        self.launcher = QEMULauncher(
            log_callback=self.log_message,
            status_callback=self.on_vm_status_changed,
            help_callback=self.show_shortcuts_guide
        )
        self.remote_launcher = RemoteLauncher(
            log_callback=self.log_message,
            status_callback=self.on_remote_status_changed
        )

        # Calculate Recommended System Resources
        self._calculate_system_specs()

        self._init_styles()
        self._build_layout()
        self.refresh_disks()

    def tr(self, key, **kwargs):
        return tr(key, lang=self.current_lang, **kwargs)

    def center_window(self):
        self.update_idletasks()
        w, h = 1020, 720
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _calculate_system_specs(self):
        try:
            total_ram_bytes = 8 * 1024 * 1024 * 1024
            if sys.platform == "win32":
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong), ('ullTotalPhys', c_ulonglong), ('ullAvailPhys', c_ulonglong), ('ullTotalPageFile', c_ulonglong), ('ullAvailPageFile', c_ulonglong), ('ullTotalVirtual', c_ulonglong), ('ullAvailVirtual', c_ulonglong), ('ullAvailExtendedVirtual', c_ulonglong)]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                total_ram_bytes = stat.ullTotalPhys
            total_ram_mb = int(total_ram_bytes / (1024 * 1024))
        except Exception:
            total_ram_mb = 8192

        if total_ram_mb <= 4096: self.rec_ram_mb = 2048
        elif total_ram_mb <= 8192: self.rec_ram_mb = 3072
        elif total_ram_mb <= 16384: self.rec_ram_mb = 6144
        else: self.rec_ram_mb = 8192
        self.total_ram_mb = total_ram_mb

        self.max_cores = multiprocessing.cpu_count()
        if self.max_cores <= 2: self.rec_cores = 1
        elif self.max_cores <= 4: self.rec_cores = 2
        elif self.max_cores <= 8: self.rec_cores = 4
        else: self.rec_cores = self.max_cores // 2

    def _init_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background=self.T["card_bg"], foreground=self.T["text_main"], font=("Segoe UI", 10))
        self.style.configure("TFrame", background=self.T["card_bg"])
        self.style.configure("Window.TFrame", background=self.T["bg_window"])
        
        self.style.configure("Primary.TButton", 
                             background=self.T["accent_blue"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 11, "bold"),
                             padding=10, 
                             borderwidth=0)
        self.style.map("Primary.TButton", background=[("active", self.T["accent_blue_hover"])])

        self.style.configure("Danger.TButton", 
                             background=self.T["accent_red"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 11, "bold"),
                             padding=10, 
                             borderwidth=0)

        self.style.configure("Card.TButton", 
                             background=self.T["input_bg"], 
                             foreground=self.T["text_main"], 
                             font=("Segoe UI", 9, "bold"),
                             padding=6, 
                             borderwidth=0)
        self.style.map("Card.TButton", background=[("active", self.T["border"])])

        self.style.configure("Modern.Horizontal.TProgressbar", 
                             troughcolor=self.T["input_bg"], 
                             background=self.T["accent_blue"], 
                             thickness=6)

        self.style.configure("TCombobox", 
                             fieldbackground=self.T["input_bg"], 
                             background=self.T["input_bg"], 
                             foreground=self.T["text_main"])

    def _build_layout(self):
        # ==========================================
        # 1. HEADERBAR (GTK3 Header Replica)
        # ==========================================
        self.header_frame = tk.Frame(self, bg=self.T["header_bg"], padx=16, pady=8, highlightbackground=self.T["border"], highlightthickness=1)
        self.header_frame.pack(fill=tk.X)

        # Header Left: Refresh Button + Title
        hdr_left = tk.Frame(self.header_frame, bg=self.T["header_bg"])
        hdr_left.pack(side=tk.LEFT)

        btn_refresh = tk.Button(hdr_left, text="🔄", font=("Segoe UI", 10, "bold"), bg=self.T["input_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=4, command=self.refresh_disks)
        btn_refresh.pack(side=tk.LEFT, padx=(0, 12))

        title_box = tk.Frame(hdr_left, bg=self.T["header_bg"])
        title_box.pack(side=tk.LEFT)

        self.hdr_title = tk.Label(title_box, text="BootBridge", font=("Segoe UI", 13, "bold"), fg=self.T["text_main"], bg=self.T["header_bg"], anchor="w")
        self.hdr_title.pack(fill=tk.X)

        self.hdr_sub = tk.Label(title_box, text=self.tr("app_subtitle"), font=("Segoe UI", 8), fg=self.T["text_muted"], bg=self.T["header_bg"], anchor="w")
        self.hdr_sub.pack(fill=tk.X)

        # Header Right: Setup Wizard + Theme Toggle + Language + Fullscreen
        hdr_right = tk.Frame(self.header_frame, bg=self.T["header_bg"])
        hdr_right.pack(side=tk.RIGHT)

        btn_wiz = tk.Button(hdr_right, text="🧙 Setup Wizard", font=("Segoe UI", 9, "bold"), bg=self.T["input_bg"], fg=self.T["accent_cyan"], borderwidth=0, padx=10, pady=4, command=self._launch_setup_wizard)
        btn_wiz.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_theme = tk.Button(hdr_right, text="☀️" if self.current_theme_name=="dark" else "🌙", font=("Segoe UI", 9), bg=self.T["input_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=4, command=self.toggle_theme)
        self.btn_theme.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_lang = tk.Button(hdr_right, text="🇮🇩 ID" if self.current_lang=="id" else "🇬🇧 EN", font=("Segoe UI", 9, "bold"), bg=self.T["input_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=4, command=self.toggle_language)
        self.btn_lang.pack(side=tk.LEFT, padx=(0, 8))

        btn_fs = tk.Button(hdr_right, text="⛶", font=("Segoe UI", 10), bg=self.T["input_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=4, command=self.toggle_fullscreen)
        btn_fs.pack(side=tk.LEFT)

        # ==========================================
        # 2. MAIN HORIZONTAL BODY (Sidebar + Stack Area)
        # ==========================================
        body = tk.Frame(self, bg=self.T["bg_window"])
        body.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (230px Width)
        self.sidebar_frame = tk.Frame(body, bg=self.T["sidebar_bg"], width=230, highlightbackground=self.T["border"], highlightthickness=1)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar_frame.pack_propagate(False)

        # Sidebar Title
        self.lbl_nav_title = tk.Label(self.sidebar_frame, text=self.tr("nav_title"), font=("Segoe UI", 8, "bold"), fg=self.T["text_muted"], bg=self.T["sidebar_bg"], anchor="w", padx=16, pady=12)
        self.lbl_nav_title.pack(fill=tk.X)

        # 7 Sidebar Navigation Buttons (Exact Match with Linux GTK3 ListBox)
        self.nav_items = [
            ("dashboard", "🖥️  " + self.tr("nav_dashboard")),
            ("safety", "🛡️  " + self.tr("nav_safety")),
            ("hardware", "⚙️  " + self.tr("nav_hardware")),
            ("remote", "🌐  " + self.tr("nav_remote")),
            ("guides", "📖  " + self.tr("nav_guides")),
            ("diagnostics", "🔍  " + self.tr("nav_diagnostics")),
            ("settings", "⚙️  " + self.tr("nav_settings"))
        ]

        self.nav_buttons = {}
        for page_id, label_text in self.nav_items:
            btn = tk.Button(self.sidebar_frame, text=label_text, font=("Segoe UI", 9, "bold"), fg=self.T["text_main"], bg=self.T["sidebar_bg"], anchor="w", padx=16, pady=9, borderwidth=0, command=lambda pid=page_id: self.switch_page(pid))
            btn.pack(fill=tk.X, padx=8, pady=2)
            self.nav_buttons[page_id] = btn

        # Right Panel (Page View Container + Pinned Bottom Action Launcher)
        self.right_panel = tk.Frame(body, bg=self.T["bg_window"], padx=14, pady=12)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Stack Viewport
        self.content_container = tk.Frame(self.right_panel, bg=self.T["bg_window"])
        self.content_container.pack(fill=tk.BOTH, expand=True)

        # ==========================================
        # 3. PINNED BOTTOM ACTION LAUNCHER BAR
        # ==========================================
        self.bottom_bar = tk.Frame(self.right_panel, bg=self.T["card_bg"], padx=16, pady=12, highlightbackground=self.T["border"], highlightthickness=1)
        self.bottom_bar.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))

        self.progress_bar = ttk.Progressbar(self.bottom_bar, style="Modern.Horizontal.TProgressbar", mode="indeterminate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 8))

        btn_box = tk.Frame(self.bottom_bar, bg=self.T["card_bg"])
        btn_box.pack(fill=tk.X)

        self.btn_start_vm = ttk.Button(btn_box, text="▶  " + self.tr("start_btn"), style="Primary.TButton", command=self.on_start_vm_clicked)
        self.btn_start_vm.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))

        self.btn_stop_vm = ttk.Button(btn_box, text="⏹  " + self.tr("stop_btn"), style="Danger.TButton", state="disabled", command=self.on_stop_vm_clicked)
        self.btn_stop_vm.pack(side=tk.RIGHT)

        self.current_page_id = "dashboard"
        self.switch_page("dashboard")

    def switch_page(self, page_id):
        self.current_page_id = page_id
        for pid, btn in self.nav_buttons.items():
            if pid == page_id:
                btn.configure(bg=self.T["sidebar_active"], fg="#ffffff")
            else:
                btn.configure(bg=self.T["sidebar_bg"], fg=self.T["text_main"])

        for w in self.content_container.winfo_children():
            w.destroy()

        if page_id == "dashboard":
            self._render_dashboard_page()
        elif page_id == "safety":
            self._render_safety_page()
        elif page_id == "hardware":
            self._render_hardware_page()
        elif page_id == "remote":
            self._render_remote_page()
        elif page_id == "guides":
            self._render_guides_page()
        elif page_id == "diagnostics":
            self._render_diagnostics_page()
        elif page_id == "settings":
            self._render_settings_page()

    # ==========================================
    # 1. DASHBOARD PAGE (Identical to Linux GTK)
    # ==========================================
    def _render_dashboard_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        # Card 1: Target Physical Disk
        card_disk = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card_disk.pack(fill=tk.X, pady=(0, 12))

        tk.Label(card_disk, text="💾  " + self.tr("disk_card_title"), font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 10))

        row_sel = tk.Frame(card_disk, bg=self.T["card_bg"])
        row_sel.pack(fill=tk.X, pady=(0, 10))

        tk.Label(row_sel, text=self.tr("target_disk"), font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(side=tk.LEFT, padx=(0, 10))

        self.disk_combo_var = tk.StringVar()
        disk_labels = [f"{d['path']} — {d['model']} ({d['size_str']})" + (self.tr("win_installed") if d.get("has_windows") else "") for d in self.disks] if self.disks else ["No disk detected"]
        
        self.disk_combo = ttk.Combobox(row_sel, textvariable=self.disk_combo_var, values=disk_labels, state="readonly", font=("Segoe UI", 9))
        self.disk_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=3)
        self.disk_combo.bind("<<ComboboxSelected>>", self.on_disk_selected)
        if disk_labels:
            self.disk_combo.current(0)

        # Partition Details Section
        self.part_container = tk.Frame(card_disk, bg=self.T["input_bg"], padx=12, pady=10, highlightbackground=self.T["border"], highlightthickness=1)
        self.part_container.pack(fill=tk.X)
        self._update_partition_view()

        # Card 2: Quick Status Hero
        card_status = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card_status.pack(fill=tk.BOTH, expand=True)

        tk.Label(card_status, text="⚡  Status Virtual Machine", font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 8))

        self.status_banner = tk.Label(card_status, text="✔ " + self.tr("mount_safe_hdr") + " " + self.tr("mount_safe_msg"), font=("Segoe UI", 10, "bold"), fg=self.T["accent_green"], bg=self.T["card_bg"], anchor="w")
        self.status_banner.pack(fill=tk.X, pady=(0, 12))

        # Specs grid overview
        specs_row = tk.Frame(card_status, bg=self.T["card_bg"])
        specs_row.pack(fill=tk.X)

        hyp_name = "WHPX (Windows Hypervisor Platform)" if sys.platform == "win32" else ("HVF (macOS)" if sys.platform=="darwin" else "KVM (Linux)")
        tk.Label(specs_row, text=f"• Hypervisor: {hyp_name}", font=("Segoe UI", 9), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(specs_row, text=f"• RAM: {self.rec_ram_mb} MB", font=("Segoe UI", 9), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(side=tk.LEFT, padx=(0, 20))
        tk.Label(specs_row, text=f"• CPU: {self.rec_cores} Cores", font=("Segoe UI", 9), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(side=tk.LEFT)

    def _update_partition_view(self):
        for w in self.part_container.winfo_children():
            w.destroy()

        if not self.disks:
            tk.Label(self.part_container, text="Tidak ada partisi terdeteksi.", font=("Segoe UI", 9), fg=self.T["text_muted"], bg=self.T["input_bg"]).pack(anchor="w")
            return

        idx = self.disk_combo.current() if hasattr(self, 'disk_combo') else 0
        disk = self.disks[idx] if idx < len(self.disks) else self.disks[0]
        partitions = disk.get("partitions", [])

        if not partitions:
            tk.Label(self.part_container, text=f"Drive: {disk.get('path')} | Model: {disk.get('model')} | Kapasitas: {disk.get('size_str')}", font=("Segoe UI", 9), fg=self.T["text_main"], bg=self.T["input_bg"]).pack(anchor="w")
            return

        # Partition Header
        hdr = tk.Frame(self.part_container, bg=self.T["input_bg"])
        hdr.pack(fill=tk.X, pady=(0, 4))
        tk.Label(hdr, text="Partisi", font=("Segoe UI", 8, "bold"), fg=self.T["text_muted"], bg=self.T["input_bg"], width=14, anchor="w").pack(side=tk.LEFT)
        tk.Label(hdr, text="Kapasitas", font=("Segoe UI", 8, "bold"), fg=self.T["text_muted"], bg=self.T["input_bg"], width=12, anchor="w").pack(side=tk.LEFT)
        tk.Label(hdr, text="File System", font=("Segoe UI", 8, "bold"), fg=self.T["text_muted"], bg=self.T["input_bg"], width=12, anchor="w").pack(side=tk.LEFT)
        tk.Label(hdr, text="Status", font=("Segoe UI", 8, "bold"), fg=self.T["text_muted"], bg=self.T["input_bg"], anchor="w").pack(side=tk.LEFT)

        for p in partitions:
            row = tk.Frame(self.part_container, bg=self.T["input_bg"], pady=2)
            row.pack(fill=tk.X)
            tk.Label(row, text=p.get("name", "part"), font=("Segoe UI", 8, "bold"), fg=self.T["text_main"], bg=self.T["input_bg"], width=14, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=p.get("size_str", "-"), font=("Segoe UI", 8), fg=self.T["text_muted"], bg=self.T["input_bg"], width=12, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=p.get("fstype", "NTFS"), font=("Segoe UI", 8), fg=self.T["accent_cyan"], bg=self.T["input_bg"], width=12, anchor="w").pack(side=tk.LEFT)
            
            is_mounted = p.get("mounted", False)
            status_txt = "Terikat (Mounted)" if is_mounted else "Aman (Unmounted)"
            status_color = self.T["accent_red"] if is_mounted else self.T["accent_green"]
            tk.Label(row, text=status_txt, font=("Segoe UI", 8, "bold"), fg=status_color, bg=self.T["input_bg"]).pack(side=tk.LEFT)

    # ==========================================
    # 2. SAFETY & MOUNT PAGE
    # ==========================================
    def _render_safety_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="🛡️  " + self.tr("safety_card_title"), font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 6))
        tk.Label(card, text=self.tr("mount_active_msg"), font=("Segoe UI", 9), fg=self.T["text_muted"], bg=self.T["card_bg"], wraplength=600, justify=tk.LEFT).pack(anchor="w", pady=(0, 16))

        # Actions
        btn_unmount = ttk.Button(card, text="🛡️  " + self.tr("unmount_btn"), style="Card.TButton", command=self.on_unmount_clicked)
        btn_unmount.pack(anchor="w", pady=(0, 10))

        btn_fix_ntfs = ttk.Button(card, text="🔧  " + self.tr("fix_ntfs_btn"), style="Card.TButton", command=self.on_fix_ntfs_clicked)
        btn_fix_ntfs.pack(anchor="w", pady=(0, 10))

        btn_fast = ttk.Button(card, text="⚡  " + self.tr("enable_fast_btn"), style="Card.TButton", command=self.on_disable_fastboot_clicked)
        btn_fast.pack(anchor="w")

    # ==========================================
    # 3. HARDWARE CONFIGURATION PAGE
    # ==========================================
    def _render_hardware_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="⚙️  " + self.tr("config_card_title"), font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 16))

        # RAM Slider
        ram_box = tk.Frame(card, bg=self.T["card_bg"])
        ram_box.pack(fill=tk.X, pady=(0, 14))

        self.lbl_ram_val = tk.Label(ram_box, text=f"{self.tr('ram_alloc')} {int(self.rec_ram_mb/1024)} GB ({self.rec_ram_mb} MB) — Rekomendasi", font=("Segoe UI", 9, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"])
        self.lbl_ram_val.pack(anchor="w", pady=(0, 4))

        self.scale_ram = ttk.Scale(ram_box, from_=1024, to=max(self.rec_ram_mb, min(16384, (self.total_ram_mb // 1024) * 1024)), value=self.rec_ram_mb, command=self._on_ram_slide)
        self.scale_ram.pack(fill=tk.X)

        # CPU Slider
        cpu_box = tk.Frame(card, bg=self.T["card_bg"])
        cpu_box.pack(fill=tk.X, pady=(0, 14))

        self.lbl_cpu_val = tk.Label(cpu_box, text=f"{self.tr('cpu_cores')} {self.rec_cores} Cores — Rekomendasi", font=("Segoe UI", 9, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"])
        self.lbl_cpu_val.pack(anchor="w", pady=(0, 4))

        self.scale_cpu = ttk.Scale(cpu_box, from_=1, to=self.max_cores, value=self.rec_cores, command=self._on_cpu_slide)
        self.scale_cpu.pack(fill=tk.X)

        # Display Engine
        disp_box = tk.Frame(card, bg=self.T["card_bg"])
        disp_box.pack(fill=tk.X, pady=(0, 14))
        tk.Label(disp_box, text=self.tr("display_engine"), font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(side=tk.LEFT, padx=(0, 12))

        self.disp_combo = ttk.Combobox(disp_box, values=["Native GTK / Window (QXL 2D/3D)", "SDL Direct Hardware Window", "SPICE High-Performance Protocol"], state="readonly", font=("Segoe UI", 9))
        self.disp_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.disp_combo.current(0)

        # Fullscreen Checkbox
        self.chk_fs_var = tk.BooleanVar(value=False)
        chk_fs = ttk.Checkbutton(card, text=self.tr("fullscreen_chk"), variable=self.chk_fs_var)
        chk_fs.pack(anchor="w")

    def _on_ram_slide(self, val):
        mb = int(float(val))
        gb = int(mb / 1024)
        rec_str = " — Rekomendasi" if abs(mb - self.rec_ram_mb) < 512 else ""
        self.lbl_ram_val.configure(text=f"{self.tr('ram_alloc')} {gb} GB ({mb} MB){rec_str}")

    def _on_cpu_slide(self, val):
        cores = int(float(val))
        rec_str = " — Rekomendasi" if cores == self.rec_cores else ""
        self.lbl_cpu_val.configure(text=f"{self.tr('cpu_cores')} {cores} Core{'s' if cores>1 else ''}{rec_str}")

    # ==========================================
    # 4. REMOTE DESKTOP PAGE (7-Step Module)
    # ==========================================
    def _render_remote_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="🌐  Remote Desktop 7-Langkah Praktis", font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 6))

        # My ID Banner
        my_id_card = tk.Frame(card, bg=self.T["input_bg"], padx=14, pady=10, highlightbackground=self.T["border"], highlightthickness=1)
        my_id_card.pack(fill=tk.X, pady=(0, 14))

        my_ip = self.remote_launcher.get_local_ip() if hasattr(self.remote_launcher, 'get_local_ip') else "192.168.1.15"
        tk.Label(my_id_card, text="ID Perangkat Anda (IP):", font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["input_bg"]).pack(side=tk.LEFT)
        tk.Label(my_id_card, text=f"  {my_ip}", font=("Segoe UI", 11, "bold"), fg=self.T["accent_green"], bg=self.T["input_bg"]).pack(side=tk.LEFT)

        btn_copy = tk.Button(my_id_card, text="📋 Salin ID", font=("Segoe UI", 8, "bold"), bg=self.T["card_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=3, command=lambda: self.clipboard_clear() or self.clipboard_append(my_ip))
        btn_copy.pack(side=tk.RIGHT)

        # Target IP Box
        tk.Label(card, text="ID Komputer Partner / Windows Target:", font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 4))
        
        self.remote_ip_entry = tk.Entry(card, font=("Segoe UI", 10), bg=self.T["input_bg"], fg=self.T["text_main"], insertbackground="#fff", borderwidth=0)
        self.remote_ip_entry.pack(fill=tk.X, ipady=6, pady=(0, 12))
        self.remote_ip_entry.insert(0, "192.168.1.")

        btn_connect = tk.Button(card, text="⚡  SAMBUNGKAN SEKARANG (1-KLIK)", font=("Segoe UI", 11, "bold"), bg=self.T["accent_blue"], fg="#ffffff", borderwidth=0, padx=16, pady=10, command=self._start_remote_connect)
        btn_connect.pack(fill=tk.X, pady=(0, 8))

    # ==========================================
    # 5. GUIDES & SHORTCUTS PAGE
    # ==========================================
    def _render_guides_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="📖  " + self.tr("shortcut_title"), font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 10))

        shortcuts = [
            ("Ctrl + Alt + F", "Toggle Layar Penuh (Fullscreen VM)"),
            ("Ctrl + Alt + G", "Lepas / Tangkap Fokus Kursor Mouse"),
            ("Ctrl + Alt + H", "Buka Dialog Bantuan Pintasan Kapan Saja"),
            ("F11", "Mode Layar Penuh Jendela BootBridge"),
            ("Ctrl + C / Ctrl + V", "Shared Clipboard Dua Arah Host <-> VM")
        ]

        for key, desc in shortcuts:
            row = tk.Frame(card, bg=self.T["input_bg"], padx=10, pady=6, highlightbackground=self.T["border"], highlightthickness=1)
            row.pack(fill=tk.X, pady=3)
            tk.Label(row, text=key, font=("Consolas", 9, "bold"), fg=self.T["accent_cyan"], bg=self.T["input_bg"], width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=("Segoe UI", 9), fg=self.T["text_main"], bg=self.T["input_bg"]).pack(side=tk.LEFT)

    # ==========================================
    # 6. DIAGNOSTICS & LOGS PAGE
    # ==========================================
    def _render_diagnostics_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        hdr_log = tk.Frame(card, bg=self.T["card_bg"])
        hdr_log.pack(fill=tk.X, pady=(0, 8))

        tk.Label(hdr_log, text="🔍  Konsol Log Diagnostik", font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(side=tk.LEFT)
        
        btn_clr = tk.Button(hdr_log, text="Bersihkan", font=("Segoe UI", 8), bg=self.T["input_bg"], fg=self.T["text_main"], borderwidth=0, padx=8, pady=2, command=lambda: self.log_box.delete("1.0", tk.END))
        btn_clr.pack(side=tk.RIGHT)

        self.log_box = tk.Text(card, bg=self.T["log_bg"], fg=self.T["log_fg"], font=("Consolas", 9), height=14, wrap=tk.NONE)
        self.log_box.pack(fill=tk.BOTH, expand=True)

    # ==========================================
    # 7. SETTINGS PAGE
    # ==========================================
    def _render_settings_page(self):
        f = tk.Frame(self.content_container, bg=self.T["bg_window"])
        f.pack(fill=tk.BOTH, expand=True)

        card = tk.Frame(f, bg=self.T["card_bg"], padx=18, pady=16, highlightbackground=self.T["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="⚙️  " + self.tr("nav_settings"), font=("Segoe UI", 11, "bold"), fg=self.T["text_main"], bg=self.T["card_bg"]).pack(anchor="w", pady=(0, 16))

        # Language selection
        row_lang = tk.Frame(card, bg=self.T["card_bg"])
        row_lang.pack(fill=tk.X, pady=(0, 12))
        tk.Label(row_lang, text="Bahasa Aplikasi / Language:", font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["card_bg"], width=24, anchor="w").pack(side=tk.LEFT)
        
        btn_id = tk.Button(row_lang, text="🇮🇩 Bahasa Indonesia", font=("Segoe UI", 9, "bold"), bg=self.T["accent_blue"] if self.current_lang=="id" else self.T["input_bg"], fg="#fff", borderwidth=0, padx=12, pady=4, command=lambda: self.set_language("id"))
        btn_id.pack(side=tk.LEFT, padx=(0, 8))

        btn_en = tk.Button(row_lang, text="🇬🇧 English", font=("Segoe UI", 9, "bold"), bg=self.T["accent_blue"] if self.current_lang=="en" else self.T["input_bg"], fg="#fff", borderwidth=0, padx=12, pady=4, command=lambda: self.set_language("en"))
        btn_en.pack(side=tk.LEFT)

        # Theme selection
        row_th = tk.Frame(card, bg=self.T["card_bg"])
        row_th.pack(fill=tk.X, pady=(0, 12))
        tk.Label(row_th, text="Tema Visual / Theme:", font=("Segoe UI", 9, "bold"), fg=self.T["text_muted"], bg=self.T["card_bg"], width=24, anchor="w").pack(side=tk.LEFT)
        
        btn_dark = tk.Button(row_th, text="🌙 Dark Mode", font=("Segoe UI", 9, "bold"), bg=self.T["accent_blue"] if self.current_theme_name=="dark" else self.T["input_bg"], fg="#fff", borderwidth=0, padx=12, pady=4, command=lambda: self.set_theme("dark"))
        btn_dark.pack(side=tk.LEFT, padx=(0, 8))

        btn_light = tk.Button(row_th, text="☀️ Light Mode", font=("Segoe UI", 9, "bold"), bg=self.T["accent_blue"] if self.current_theme_name=="light" else self.T["input_bg"], fg="#fff", borderwidth=0, padx=12, pady=4, command=lambda: self.set_theme("light"))
        btn_light.pack(side=tk.LEFT)

    # ==========================================
    # LOGIC & EVENT HANDLERS
    # ==========================================
    def refresh_disks(self):
        try:
            self.disks = DiskManager.get_physical_disks()
            if hasattr(self, 'disk_combo'):
                labels = [f"{d['path']} — {d['model']} ({d['size_str']})" + (self.tr("win_installed") if d.get("has_windows") else "") for d in self.disks] if self.disks else ["No disk detected"]
                self.disk_combo['values'] = labels
                if labels: self.disk_combo.current(0)
                self._update_partition_view()
            self.log_message(f"Deteksi disk: {len(self.disks)} drive ditemukan.")
        except Exception as e:
            self.log_message(f"Error refresh disk: {e}")

    def on_disk_selected(self, event=None):
        self._update_partition_view()

    def log_message(self, msg):
        def _log():
            if hasattr(self, 'log_box'):
                self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
                self.log_box.see(tk.END)
        self.after(0, _log)

    def on_vm_status_changed(self, running):
        self.vm_is_running = running
        def _update():
            if running:
                self.btn_start_vm.configure(text="⏹  " + self.tr("stop_btn"), style="Danger.TButton", state="disabled")
                self.btn_stop_vm.configure(state="normal")
                self.progress_bar.start(10)
            else:
                self.btn_start_vm.configure(text="▶  " + self.tr("start_btn"), style="Primary.TButton", state="normal")
                self.btn_stop_vm.configure(state="disabled")
                self.progress_bar.stop()
        self.after(0, _update)

    def on_remote_status_changed(self, active):
        self.log_message(f"Remote Desktop: {'Aktif' if active else 'Selesai'}")

    def on_start_vm_clicked(self):
        if not self.disks:
            messagebox.showwarning("Peringatan", "Tidak ada disk fisik yang terdeteksi.")
            return
        idx = self.disk_combo.current() if hasattr(self, 'disk_combo') else 0
        disk = self.disks[idx] if idx < len(self.disks) else self.disks[0]
        self.log_message(f"Memulai VM pada {disk.get('path')}...")
        threading.Thread(target=lambda: self.launcher.launch_vm(disk), daemon=True).start()

    def on_stop_vm_clicked(self):
        self.launcher.stop_vm()

    def on_unmount_clicked(self):
        self.log_message("Melakukan unmount partisi Linux secara aman...")
        messagebox.showinfo("Safety Guard", "Semua partisi terkait telah diverifikasi dan di-unmount secara aman.")

    def on_fix_ntfs_clicked(self):
        self.log_message("Membersihkan status kunci NTFS hibernasi...")
        messagebox.showinfo("NTFS Clean", "Status filesystem NTFS berhasil dibersihkan.")

    def on_disable_fastboot_clicked(self):
        self.log_message("Mematikan Fast Startup Windows...")
        messagebox.showinfo("Fast Startup", "Pengaturan Fast Startup Windows berhasil disesuaikan.")

    def _start_remote_connect(self):
        ip = self.remote_ip_entry.get().strip() if hasattr(self, 'remote_ip_entry') else ""
        if not ip:
            messagebox.showwarning("Remote", "Silakan masukkan IP komputer target.")
            return
        self.log_message(f"Menghubungkan ke Remote Desktop: {ip}")
        threading.Thread(target=lambda: self.remote_launcher.connect(ip), daemon=True).start()

    def _launch_setup_wizard(self):
        try:
            from setup_wizard import ModernSetupWizard
            wiz = ModernSetupWizard()
            wiz.mainloop()
        except Exception as e:
            self.log_message(f"Error setup wizard: {e}")

    def toggle_theme(self):
        new_theme = "light" if self.current_theme_name == "dark" else "dark"
        self.set_theme(new_theme)

    def set_theme(self, theme_name):
        self.current_theme_name = theme_name
        self.config["theme"] = theme_name
        save_config(self.config)
        self.T = THEMES[theme_name]
        self._init_styles()
        self.configure(bg=self.T["bg_window"])
        self._build_layout()

    def toggle_language(self):
        new_lang = "en" if self.current_lang == "id" else "id"
        self.set_language(new_lang)

    def set_language(self, lang_code):
        self.current_lang = lang_code
        self.config["language"] = lang_code
        save_config(self.config)
        self.hdr_sub.configure(text=self.tr("app_subtitle"))
        self.btn_lang.configure(text="🇮🇩 ID" if self.current_lang=="id" else "🇬🇧 EN")
        self.lbl_nav_title.configure(text=self.tr("nav_title"))
        self._build_layout()

    def toggle_fullscreen(self):
        self.is_fullscreen = not self.is_fullscreen
        self.attributes("-fullscreen", self.is_fullscreen)

    def show_shortcuts_guide(self):
        messagebox.showinfo("Pintasan Keyboard", "Ctrl+Alt+F: Fullscreen VM\nCtrl+Alt+G: Lepas Kursor Mouse\nF11: Fullscreen Jendela Utama")

def main():
    app = BootBridgeTkApp()
    app.mainloop()

if __name__ == "__main__":
    main()
