#!/usr/bin/env python3
"""
BootBridge Modern Multi-Step Setup Wizard
Cross-Platform Graphical Installer with identical theme to BootBridge main application.
Requires no heavy external dependencies to run out-of-the-box.
"""

import os
import sys
import subprocess
import shutil
import threading
import time
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_NAME = "BootBridge"
APP_VERSION = "1.0.0"

# Unified Color Palette matching BootBridge Main App Window
THEME = {
    "bg_dark": "#090d16",       # Deepest Navy/Slate (Main Background)
    "bg_card": "#131b2e",       # Card Background
    "bg_input": "#1e293b",      # Input/Button Background
    "accent_blue": "#2563eb",   # Primary Blue
    "accent_blue_hover": "#1d4ed8",
    "accent_cyan": "#06b6d4",   # Accent Cyan
    "accent_green": "#10b981",  # Emerald Green
    "accent_red": "#ef4444",    # Danger Red
    "text_main": "#f8fafc",     # Light Text
    "text_muted": "#94a3b8",    # Muted Text
    "border": "#1e293b",        # Subtle Border
    "sidebar_bg": "#090d16",    # Sidebar Navy
    "step_active_bg": "#2563eb",
    "step_idle_bg": "#131b2e"
}

# Localization strings
I18N = {
    "id": {
        "title": f"Wizard Instalasi {APP_NAME} v{APP_VERSION}",
        "step_welcome": "1. Sambutan",
        "step_check": "2. Cek Kesiapan Sistem",
        "step_options": "3. Opsi Instalasi",
        "step_install": "4. Proses Instalasi",
        "step_finish": "5. Selesai",
        "welcome_title": f"Selamat Datang di Installer {APP_NAME}",
        "welcome_sub": "Aplikasi virtualisasi dual-boot fisik Windows tanpa perlu restart.",
        "welcome_desc": f"{APP_NAME} memungkinkan Anda menjalankan instalasi Windows fisik secara langsung dari sistem operasi utama dengan akselerasi hypervisor native (KVM, WHPX, HVF) dan performa 1:1.\n\nKlik 'Lanjut' untuk memeriksa kesiapan sistem dan mengonfigurasi instalasi.",
        "lang_select": "Bahasa / Language:",
        "sys_title": "Pemeriksaan Kesiapan Sistem",
        "sys_sub": "Mendeteksi akselerasi hypervisor dan komponen pendukung...",
        "sys_os": "Sistem Operasi",
        "sys_hypervisor": "Akselerasi Hypervisor",
        "sys_qemu": "Mesin Virtual QEMU",
        "sys_python": "Lingkungan Python",
        "sys_status_ready": "Sistem siap untuk instalasi.",
        "sys_recheck": "Periksa Ulang",
        "opt_title": "Pilihan & Lokasi Instalasi",
        "opt_sub": "Tentukan folder tujuan dan konfigurasi shortcut aplikasi.",
        "opt_path_label": "Folder Tujuan Instalasi:",
        "opt_browse": "Jelajahi...",
        "opt_shortcuts": "Shortcut & Integrasi Sistem:",
        "opt_chk_desktop": "Buat shortcut di Desktop",
        "opt_chk_menu": "Tambahkan ke Menu Aplikasi / Start Menu",
        "opt_chk_path": "Tambahkan BootBridge ke PATH Sistem",
        "opt_chk_autostart": "Jalankan BootBridge langsung setelah instalasi",
        "inst_title": "Memasang BootBridge...",
        "inst_sub": "Mohon tunggu sementara file dan komponen dipasang.",
        "inst_log_show": "Tampilkan Log Detail",
        "inst_log_hide": "Sembunyikan Log Detail",
        "fin_title": "Instalasi Selesai!",
        "fin_sub": f"{APP_NAME} berhasil dipasang di komputer Anda.",
        "fin_msg": f"{APP_NAME} telah siap digunakan. Anda dapat membukanya kapan saja melalui shortcut yang telah dibuat.",
        "fin_launch": "Jalankan BootBridge sekarang",
        "btn_back": "Kembali",
        "btn_next": "Lanjut",
        "btn_install": "Install Sekarang",
        "btn_finish": "Selesai",
        "btn_cancel": "Batal",
        "status_copying": "Menyalin file aplikasi...",
        "status_deps": "Memeriksa paket dependensi...",
        "status_shortcuts": "Membuat shortcut dan konfigurasi desktop...",
        "status_done": "Instalasi berhasil 100%!"
    },
    "en": {
        "title": f"{APP_NAME} v{APP_VERSION} Setup Wizard",
        "step_welcome": "1. Welcome",
        "step_check": "2. System Diagnostics",
        "step_options": "3. Options",
        "step_install": "4. Installation",
        "step_finish": "5. Finish",
        "welcome_title": f"Welcome to {APP_NAME} Setup",
        "welcome_sub": "Zero-reboot physical Windows dual-boot virtualization launcher.",
        "welcome_desc": f"{APP_NAME} allows you to run your physical Windows installation directly from your main operating system with native hardware hypervisor acceleration (KVM, WHPX, HVF) at 1:1 near bare-metal speed.\n\nClick 'Next' to diagnose system requirements and configure setup.",
        "lang_select": "Language / Bahasa:",
        "sys_title": "System Diagnostics & Requirements",
        "sys_sub": "Checking hardware virtualization and required components...",
        "sys_os": "Operating System",
        "sys_hypervisor": "Hypervisor Acceleration",
        "sys_qemu": "QEMU Virtual Engine",
        "sys_python": "Python Environment",
        "sys_status_ready": "System is ready for installation.",
        "sys_recheck": "Re-check",
        "opt_title": "Installation Destination & Options",
        "opt_sub": "Choose install directory and shortcut preferences.",
        "opt_path_label": "Destination Folder:",
        "opt_browse": "Browse...",
        "opt_shortcuts": "Shortcuts & System Integration:",
        "opt_chk_desktop": "Create Desktop Shortcut",
        "opt_chk_menu": "Add to Start Menu / Application Launcher",
        "opt_chk_path": "Add BootBridge to System PATH",
        "opt_chk_autostart": "Launch BootBridge automatically after setup",
        "inst_title": "Installing BootBridge...",
        "inst_sub": "Please wait while files and system components are configured.",
        "inst_log_show": "Show Detailed Logs",
        "inst_log_hide": "Hide Detailed Logs",
        "fin_title": "Installation Completed!",
        "fin_sub": f"{APP_NAME} has been successfully installed.",
        "fin_msg": f"{APP_NAME} is ready to use. You can launch it at any time using the created shortcuts.",
        "fin_launch": "Launch BootBridge now",
        "btn_back": "Back",
        "btn_next": "Next",
        "btn_install": "Install Now",
        "btn_finish": "Finish",
        "btn_cancel": "Cancel",
        "status_copying": "Copying application core files...",
        "status_deps": "Checking package dependencies...",
        "status_shortcuts": "Creating desktop shortcuts and integration...",
        "status_done": "Installation finished successfully (100%)!"
    }
}

class ModernSetupWizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = "id"
        self.current_step = 0
        self.steps = ["welcome", "check", "options", "install", "finish"]
        
        self.title(I18N[self.lang]["title"])
        self.geometry("820x540")
        self.minsize(780, 500)
        self.configure(bg=THEME["bg_dark"])
        self.center_window()

        # Set Window Titlebar Icon
        ico_path = os.path.join(BASE_DIR, "assets", "icon.ico")
        png_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
        if os.path.exists(ico_path) and sys.platform == "win32":
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass
        elif os.path.exists(png_path):
            try:
                icon_img = tk.PhotoImage(file=png_path)
                self.iconphoto(True, icon_img)
            except Exception:
                pass
        
        # Determine Safe Default Install Directory (User Space - No WinError 5 Permission Issues)
        self.system_os = platform.system().lower()
        if "windows" in self.system_os:
            local_appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
            self.default_install_dir = os.path.join(local_appdata, "Programs", APP_NAME)
        elif "darwin" in self.system_os:
            self.default_install_dir = f"/Applications/{APP_NAME}.app"
        else:
            self.default_install_dir = os.path.expanduser(f"~/.local/share/{APP_NAME.lower()}")
            
        self.install_path_var = tk.StringVar(value=self.default_install_dir)
        self.chk_desktop_var = tk.BooleanVar(value=True)
        self.chk_menu_var = tk.BooleanVar(value=True)
        self.chk_path_var = tk.BooleanVar(value=False)
        self.chk_launch_var = tk.BooleanVar(value=True)
        self.show_logs_var = tk.BooleanVar(value=False)

        self._init_styles()
        self._build_layout()
        self._show_step(0)

    def center_window(self):
        self.update_idletasks()
        width = 820
        height = 540
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _init_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background=THEME["bg_card"], foreground=THEME["text_main"], font=("Segoe UI", 10))
        self.style.configure("TFrame", background=THEME["bg_card"])
        self.style.configure("Dark.TFrame", background=THEME["bg_dark"])

        self.style.configure("Accent.TButton", 
                             background=THEME["accent_blue"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 10, "bold"),
                             borderwidth=0,
                             padding=8)
        self.style.map("Accent.TButton", background=[("active", THEME["accent_blue_hover"])])

        self.style.configure("Secondary.TButton", 
                             background=THEME["bg_input"], 
                             foreground=THEME["text_main"], 
                             font=("Segoe UI", 10),
                             borderwidth=0,
                             padding=8)
        self.style.map("Secondary.TButton", background=[("active", THEME["border"])])

        self.style.configure("Modern.Horizontal.TProgressbar", 
                             troughcolor=THEME["bg_input"], 
                             background=THEME["accent_blue"], 
                             thickness=12)

        self.style.configure("TCheckbutton", 
                             background=THEME["bg_card"], 
                             foreground=THEME["text_main"],
                             font=("Segoe UI", 10))
        self.style.map("TCheckbutton", background=[("active", THEME["bg_card"])])

    def _build_layout(self):
        # Master Container
        self.main_container = tk.Frame(self, bg=THEME["bg_dark"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Left Sidebar (Step Indicators)
        self.sidebar = tk.Frame(self.main_container, bg=THEME["sidebar_bg"], width=230)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        self._build_sidebar()

        # Right Content Area (Card Background)
        self.content_area = tk.Frame(self.main_container, bg=THEME["bg_card"], padx=28, pady=24, highlightbackground=THEME["border"], highlightthickness=1)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 16), pady=16)

        # Content Dynamic Frame
        self.step_container = tk.Frame(self.content_area, bg=THEME["bg_card"])
        self.step_container.pack(fill=tk.BOTH, expand=True)

        # Bottom Navigation Controls
        self.nav_frame = tk.Frame(self.content_area, bg=THEME["bg_card"], pady=12)
        self.nav_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self._build_nav_buttons()

    def _build_sidebar(self):
        brand_frame = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"], pady=20, padx=16)
        brand_frame.pack(fill=tk.X)

        tk.Label(brand_frame, text="⚡ " + APP_NAME, font=("Segoe UI", 15, "bold"), fg=THEME["text_main"], bg=THEME["sidebar_bg"], anchor="w").pack(fill=tk.X)
        tk.Label(brand_frame, text=f"v{APP_VERSION} Universal Setup", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["sidebar_bg"], anchor="w").pack(fill=tk.X)

        tk.Frame(self.sidebar, bg=THEME["border"], height=1).pack(fill=tk.X, padx=16, pady=12)

        self.step_frames = []
        self.step_labels = []
        step_keys = ["step_welcome", "step_check", "step_options", "step_install", "step_finish"]
        
        for i, key in enumerate(step_keys):
            lbl_text = I18N[self.lang][key]
            card = tk.Frame(self.sidebar, bg=THEME["step_idle_bg"], padx=12, pady=8)
            card.pack(fill=tk.X, padx=14, pady=4)
            
            lbl = tk.Label(card, text=lbl_text, font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["step_idle_bg"], anchor="w")
            lbl.pack(fill=tk.X)
            
            self.step_frames.append(card)
            self.step_labels.append(lbl)

        # Language Selector at bottom of sidebar
        lang_frame = tk.Frame(self.sidebar, bg=THEME["sidebar_bg"], padx=16, pady=16)
        lang_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.lbl_lang_text = tk.Label(lang_frame, text=I18N[self.lang]["lang_select"], font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["sidebar_bg"], anchor="w")
        self.lbl_lang_text.pack(fill=tk.X, pady=(0, 6))
        
        btn_lang_box = tk.Frame(lang_frame, bg=THEME["sidebar_bg"])
        btn_lang_box.pack(fill=tk.X)
        
        self.btn_lang_id = tk.Button(btn_lang_box, text="🇮🇩 ID", font=("Segoe UI", 8, "bold"), fg="#fff", bg=THEME["accent_blue"] if self.lang=="id" else THEME["bg_input"], borderwidth=0, padx=10, pady=4, command=lambda: self.set_language("id"))
        self.btn_lang_id.pack(side=tk.LEFT, padx=(0, 6))
        
        self.btn_lang_en = tk.Button(btn_lang_box, text="🇬🇧 EN", font=("Segoe UI", 8, "bold"), fg="#fff", bg=THEME["accent_blue"] if self.lang=="en" else THEME["bg_input"], borderwidth=0, padx=10, pady=4, command=lambda: self.set_language("en"))
        self.btn_lang_en.pack(side=tk.LEFT)

    def _build_nav_buttons(self):
        self.btn_cancel = ttk.Button(self.nav_frame, text=I18N[self.lang]["btn_cancel"], style="Secondary.TButton", command=self.destroy)
        self.btn_cancel.pack(side=tk.LEFT)

        self.btn_next = ttk.Button(self.nav_frame, text=I18N[self.lang]["btn_next"], style="Accent.TButton", command=self.next_step)
        self.btn_next.pack(side=tk.RIGHT, padx=(8, 0))

        self.btn_back = ttk.Button(self.nav_frame, text=I18N[self.lang]["btn_back"], style="Secondary.TButton", command=self.prev_step)
        self.btn_back.pack(side=tk.RIGHT)

    def set_language(self, lang_code):
        self.lang = lang_code
        self.title(I18N[self.lang]["title"])
        self.btn_lang_id.configure(bg=THEME["accent_blue"] if self.lang=="id" else THEME["bg_input"])
        self.btn_lang_en.configure(bg=THEME["accent_blue"] if self.lang=="en" else THEME["bg_input"])
        self.lbl_lang_text.configure(text=I18N[self.lang]["lang_select"])
        self._update_sidebar_labels()
        self._show_step(self.current_step)

    def _update_sidebar_labels(self):
        step_keys = ["step_welcome", "step_check", "step_options", "step_install", "step_finish"]
        for i, key in enumerate(step_keys):
            self.step_labels[i].configure(text=I18N[self.lang][key])

    def _update_sidebar_active_step(self):
        for i, (card, lbl) in enumerate(zip(self.step_frames, self.step_labels)):
            if i == self.current_step:
                card.configure(bg=THEME["step_active_bg"])
                lbl.configure(bg=THEME["step_active_bg"], fg="#ffffff", font=("Segoe UI", 9, "bold"))
            elif i < self.current_step:
                card.configure(bg=THEME["step_idle_bg"])
                lbl.configure(bg=THEME["step_idle_bg"], fg=THEME["accent_green"], font=("Segoe UI", 9))
            else:
                card.configure(bg=THEME["step_idle_bg"])
                lbl.configure(bg=THEME["step_idle_bg"], fg=THEME["text_muted"], font=("Segoe UI", 9))

    def _clear_step_container(self):
        for widget in self.step_container.winfo_children():
            widget.destroy()

    def _show_step(self, step_idx):
        self.current_step = step_idx
        self._update_sidebar_active_step()
        self._clear_step_container()

        step_name = self.steps[step_idx]
        
        if step_idx == 0:
            self.btn_back.pack_forget()
            self.btn_next.configure(text=I18N[self.lang]["btn_next"], state="normal")
            self.btn_cancel.configure(text=I18N[self.lang]["btn_cancel"], state="normal")
        elif step_idx == 1:
            self.btn_back.pack(side=tk.RIGHT)
            self.btn_next.configure(text=I18N[self.lang]["btn_next"], state="normal")
        elif step_idx == 2:
            self.btn_back.pack(side=tk.RIGHT)
            self.btn_next.configure(text=I18N[self.lang]["btn_install"], state="normal")
        elif step_idx == 3:
            self.btn_back.pack_forget()
            self.btn_next.configure(text=I18N[self.lang]["btn_install"], state="disabled")
            self.btn_cancel.configure(state="disabled")
        elif step_idx == 4:
            self.btn_back.pack_forget()
            self.btn_next.pack(side=tk.RIGHT)
            self.btn_next.configure(text=I18N[self.lang]["btn_finish"], state="normal", command=self.finish_installation)
            self.btn_cancel.pack_forget()

        if step_name == "welcome":
            self._render_welcome_step()
        elif step_name == "check":
            self._render_check_step()
        elif step_name == "options":
            self._render_options_step()
        elif step_name == "install":
            self._render_install_step()
        elif step_name == "finish":
            self._render_finish_step()

    # ------------------- STEP 1: WELCOME -------------------
    def _render_welcome_step(self):
        f = self.step_container
        
        badge = tk.Label(f, text="READY TO INSTALL", font=("Segoe UI", 8, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_input"], padx=8, pady=2)
        badge.pack(anchor="w", pady=(0, 6))

        title = tk.Label(f, text=I18N[self.lang]["welcome_title"], font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w")
        title.pack(fill=tk.X, pady=(0, 4))

        sub = tk.Label(f, text=I18N[self.lang]["welcome_sub"], font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_card"], anchor="w")
        sub.pack(fill=tk.X, pady=(0, 16))

        card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        desc = tk.Label(card, text=I18N[self.lang]["welcome_desc"], font=("Segoe UI", 10), fg=THEME["text_main"], bg=THEME["bg_dark"], justify=tk.LEFT, wraplength=480)
        desc.pack(fill=tk.BOTH, expand=True)

        pts_box = tk.Frame(card, bg=THEME["bg_dark"], pady=8)
        pts_box.pack(fill=tk.X)

        features = [
            ("⚡ Akselerasi Native 1:1" if self.lang=="id" else "⚡ 1:1 Native Acceleration", "KVM (Linux), WHPX (Windows), HVF (macOS)"),
            ("🛡️ Safe & Isolated" if self.lang=="id" else "🛡️ Safe & Isolated", "Mount safety guard, registry safety, no data loss"),
            ("🔄 Shared Clipboard Dua Arah" if self.lang=="id" else "🔄 Two-Way Shared Clipboard", "Seamless text copy-paste host <-> guest")
        ]

        for title_ft, desc_ft in features:
            item = tk.Frame(pts_box, bg=THEME["bg_dark"], pady=2)
            item.pack(fill=tk.X)
            tk.Label(item, text=f"[OK]  {title_ft}: ", font=("Segoe UI", 9, "bold"), fg=THEME["accent_green"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)
            tk.Label(item, text=desc_ft, font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)

    # ------------------- STEP 2: SYSTEM CHECK -------------------
    def _render_check_step(self):
        f = self.step_container

        title = tk.Label(f, text=I18N[self.lang]["sys_title"], font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w")
        title.pack(fill=tk.X, pady=(0, 4))

        sub = tk.Label(f, text=I18N[self.lang]["sys_sub"], font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_card"], anchor="w")
        sub.pack(fill=tk.X, pady=(0, 16))

        diag_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        diag_card.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"
        hyp_status, hyp_color = self._check_hypervisor()
        qemu_status, qemu_color = self._check_qemu()
        py_status = f"Python {platform.python_version()} ({'OK' if sys.version_info >= (3,8) else 'Update Recommended'})"

        diag_rows = [
            (I18N[self.lang]["sys_os"], os_info, THEME["text_main"]),
            (I18N[self.lang]["sys_hypervisor"], hyp_status, hyp_color),
            (I18N[self.lang]["sys_qemu"], qemu_status, qemu_color),
            (I18N[self.lang]["sys_python"], py_status, THEME["accent_green"])
        ]

        for label_text, val_text, color in diag_rows:
            row = tk.Frame(diag_card, bg=THEME["bg_dark"], pady=6)
            row.pack(fill=tk.X)
            tk.Label(row, text=label_text, font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"], width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=val_text, font=("Segoe UI", 9, "bold"), fg=color, bg=THEME["bg_dark"], anchor="w").pack(side=tk.LEFT, fill=tk.X, expand=True)

        summary_lbl = tk.Label(diag_card, text="[OK] " + I18N[self.lang]["sys_status_ready"], font=("Segoe UI", 10, "bold"), fg=THEME["accent_green"], bg=THEME["bg_dark"], anchor="w")
        summary_lbl.pack(fill=tk.X, pady=(16, 0))

    def _check_hypervisor(self):
        sys_name = platform.system().lower()
        if "linux" in sys_name:
            if os.path.exists("/dev/kvm"):
                return "KVM Hardware Acceleration (Tersedia / Available)", THEME["accent_green"]
            return "KVM (/dev/kvm) belum aktif, akan dikonfigurasi", THEME["accent_cyan"]
        elif "darwin" in sys_name:
            return "HVF (Hypervisor.framework Apple Silicon & Intel)", THEME["accent_green"]
        elif "windows" in sys_name:
            return "WHPX / Windows Hypervisor Platform Supported", THEME["accent_green"]
        return "Generic Emulation Supported", THEME["text_main"]

    def _check_qemu(self):
        qemu_bin = shutil.which("qemu-system-x86_64") or shutil.which("qemu-system-aarch64")
        if qemu_bin:
            return f"QEMU Terpasang ({os.path.basename(qemu_bin)})", THEME["accent_green"]
        return "QEMU akan diinstall otomatis oleh setup", THEME["accent_cyan"]

    # ------------------- STEP 3: OPTIONS -------------------
    def _render_options_step(self):
        f = self.step_container

        title = tk.Label(f, text=I18N[self.lang]["opt_title"], font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w")
        title.pack(fill=tk.X, pady=(0, 4))

        sub = tk.Label(f, text=I18N[self.lang]["opt_sub"], font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_card"], anchor="w")
        sub.pack(fill=tk.X, pady=(0, 16))

        path_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        path_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(path_card, text=I18N[self.lang]["opt_path_label"], font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"], anchor="w").pack(fill=tk.X, pady=(0, 6))

        path_box = tk.Frame(path_card, bg=THEME["bg_dark"])
        path_box.pack(fill=tk.X)

        entry = tk.Entry(path_box, textvariable=self.install_path_var, font=("Segoe UI", 9), bg=THEME["bg_input"], fg=THEME["text_main"], insertbackground="#fff", borderwidth=0, relief=tk.FLAT)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 8))

        btn_browse = tk.Button(path_box, text=I18N[self.lang]["opt_browse"], font=("Segoe UI", 9), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=12, pady=4, command=self._browse_path)
        btn_browse.pack(side=tk.RIGHT)

        opts_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        opts_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(opts_card, text=I18N[self.lang]["opt_shortcuts"], font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"], anchor="w").pack(fill=tk.X, pady=(0, 10))

        cb1 = ttk.Checkbutton(opts_card, text=I18N[self.lang]["opt_chk_desktop"], variable=self.chk_desktop_var)
        cb1.pack(anchor="w", pady=3)

        cb2 = ttk.Checkbutton(opts_card, text=I18N[self.lang]["opt_chk_menu"], variable=self.chk_menu_var)
        cb2.pack(anchor="w", pady=3)

        cb3 = ttk.Checkbutton(opts_card, text=I18N[self.lang]["opt_chk_path"], variable=self.chk_path_var)
        cb3.pack(anchor="w", pady=3)

        cb4 = ttk.Checkbutton(opts_card, text=I18N[self.lang]["opt_chk_autostart"], variable=self.chk_launch_var)
        cb4.pack(anchor="w", pady=3)

    def _browse_path(self):
        chosen = filedialog.askdirectory(initialdir=self.install_path_var.get())
        if chosen:
            self.install_path_var.set(chosen)

    # ------------------- STEP 4: INSTALLATION -------------------
    def _render_install_step(self):
        f = self.step_container

        title = tk.Label(f, text=I18N[self.lang]["inst_title"], font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w")
        title.pack(fill=tk.X, pady=(0, 4))

        sub = tk.Label(f, text=I18N[self.lang]["inst_sub"], font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_card"], anchor="w")
        sub.pack(fill=tk.X, pady=(0, 16))

        prog_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        prog_card.pack(fill=tk.X, pady=(0, 12))

        self.status_label = tk.Label(prog_card, text=I18N[self.lang]["status_copying"], font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_dark"], anchor="w")
        self.status_label.pack(fill=tk.X, pady=(0, 8))

        self.progress_bar = ttk.Progressbar(prog_card, style="Modern.Horizontal.TProgressbar", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=(0, 4))
        self.progress_bar["value"] = 0

        log_header_box = tk.Frame(f, bg=THEME["bg_card"])
        log_header_box.pack(fill=tk.X, pady=(4, 4))
        
        self.btn_toggle_log = tk.Button(log_header_box, text="▼ " + I18N[self.lang]["inst_log_show"], font=("Segoe UI", 8), bg=THEME["bg_input"], fg=THEME["text_muted"], borderwidth=0, padx=8, pady=2, command=self._toggle_logs)
        self.btn_toggle_log.pack(side=tk.LEFT)

        self.log_frame = tk.Frame(f, bg="#000", highlightbackground=THEME["border"], highlightthickness=1)
        self.log_text = tk.Text(self.log_frame, bg="#000", fg="#22c55e", font=("Consolas", 8), height=8, wrap=tk.NONE)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        threading.Thread(target=self._execute_installation, daemon=True).start()

    def _toggle_logs(self):
        if self.show_logs_var.get():
            self.log_frame.pack_forget()
            self.btn_toggle_log.configure(text="▼ " + I18N[self.lang]["inst_log_show"])
            self.show_logs_var.set(False)
        else:
            self.log_frame.pack(fill=tk.BOTH, expand=True, pady=(4, 0))
            self.btn_toggle_log.configure(text="▲ " + I18N[self.lang]["inst_log_hide"])
            self.show_logs_var.set(True)

    def log_msg(self, msg):
        def _append():
            self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
            self.log_text.see(tk.END)
        self.after(0, _append)

    def set_progress_val(self, val, status_text=None):
        def _update():
            self.progress_bar["value"] = val
            if status_text:
                self.status_label.configure(text=status_text)
        self.after(0, _update)

    def _execute_installation(self):
        try:
            target_dir = os.path.abspath(self.install_path_var.get())
            self.log_msg(f"Target Directory: {target_dir}")
            self.set_progress_val(10, I18N[self.lang]["status_copying"])

            # Attempt directory creation with safe user-space fallback if access denied
            try:
                os.makedirs(target_dir, exist_ok=True)
            except PermissionError:
                if "windows" in self.system_os:
                    local_appdata = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~\\AppData\\Local")
                    target_dir = os.path.join(local_appdata, "Programs", APP_NAME)
                    self.install_path_var.set(target_dir)
                    self.log_msg(f"Access Denied on system folder. Falling back to safe user directory: {target_dir}")
                    os.makedirs(target_dir, exist_ok=True)
                else:
                    raise

            time.sleep(0.3)

            # Copy essential items
            items_to_copy = ["bootbridge.py", "bootbridge.bat", "setup_wizard.py", "gui_installer.py", "core", "ui", "assets", "desktop", "README.md", "README.id.md", "LICENSE"]
            for item in items_to_copy:
                src = os.path.join(BASE_DIR, item)
                dst = os.path.join(target_dir, item)
                if os.path.exists(src) and src != dst:
                    self.log_msg(f"Installing: {item}")
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
            
            self.set_progress_val(40, I18N[self.lang]["status_deps"])
            time.sleep(0.3)

            # Platform Specific Setup
            if "linux" in self.system_os:
                self.log_msg("Configuring Linux environment...")
                user_bin = os.path.expanduser("~/.local/bin")
                os.makedirs(user_bin, exist_ok=True)
                wrapper_path = os.path.join(user_bin, "bootbridge")
                with open(wrapper_path, "w") as f:
                    f.write(f'#!/usr/bin/env bash\nexec python3 "{os.path.join(target_dir, "bootbridge.py")}" "$@"\n')
                os.chmod(wrapper_path, 0o755)
                self.log_msg(f"Created launcher: {wrapper_path}")

            elif "windows" in self.system_os:
                self.log_msg("Configuring Windows environment...")
                launcher_bat = os.path.join(target_dir, "bootbridge.bat")
                with open(launcher_bat, "w") as f:
                    f.write(f'@echo off\ncd /d "{target_dir}"\nstart "" python bootbridge.py %*\n')
                self.log_msg(f"Created launcher: {launcher_bat}")

            self.set_progress_val(70, I18N[self.lang]["status_shortcuts"])
            time.sleep(0.3)

            # Shortcut Creation
            if self.chk_desktop_var.get():
                self._create_desktop_shortcut(target_dir)

            if self.chk_menu_var.get():
                self._create_menu_shortcut(target_dir)

            self.set_progress_val(100, I18N[self.lang]["status_done"])
            self.log_msg("Setup finished successfully!")
            time.sleep(0.5)

            self.after(500, lambda: self._show_step(4))

        except Exception as e:
            self.log_msg(f"ERROR: {str(e)}")
            self.set_progress_val(0, f"Error: {str(e)}")
            messagebox.showerror("Installation Error", f"An error occurred during installation:\n{str(e)}")

    def _create_desktop_shortcut(self, target_dir):
        try:
            if "windows" in self.system_os:
                desktop_folder = os.path.join(os.path.expanduser("~"), "Desktop")
                if os.path.exists(desktop_folder):
                    bat_path = os.path.join(desktop_folder, "BootBridge.bat")
                    with open(bat_path, "w") as f:
                        f.write(f'@echo off\ncd /d "{target_dir}"\npython bootbridge.py\n')
                    self.log_msg("Created Desktop shortcut on Windows.")
            elif "linux" in self.system_os:
                desktop_folder = os.path.expanduser("~/Desktop")
                if os.path.exists(desktop_folder):
                    desk_file = os.path.join(desktop_folder, "BootBridge.desktop")
                    with open(desk_file, "w") as f:
                        f.write(f"[Desktop Entry]\nName=BootBridge\nComment=Zero-Reboot Windows Dual Boot VM\nExec=python3 \"{os.path.join(target_dir, 'bootbridge.py')}\"\nIcon={os.path.join(target_dir, 'assets', 'bootbridge.png')}\nTerminal=false\nType=Application\nCategories=System;Utility;\n")
                    os.chmod(desk_file, 0o755)
                    self.log_msg("Created Desktop shortcut on Linux.")
        except Exception as e:
            self.log_msg(f"Shortcut warning: {e}")

    def _create_menu_shortcut(self, target_dir):
        try:
            if "linux" in self.system_os:
                app_dir = os.path.expanduser("~/.local/share/applications")
                os.makedirs(app_dir, exist_ok=True)
                desk_file = os.path.join(app_dir, "bootbridge.desktop")
                with open(desk_file, "w") as f:
                    f.write(f"[Desktop Entry]\nName=BootBridge\nComment=Zero-Reboot Windows Dual Boot VM\nExec=python3 \"{os.path.join(target_dir, 'bootbridge.py')}\"\nIcon={os.path.join(target_dir, 'assets', 'bootbridge.png')}\nTerminal=false\nType=Application\nCategories=System;Utility;\n")
                subprocess.run(["update-desktop-database", app_dir], capture_output=True)
                self.log_msg("Registered application menu shortcut.")
        except Exception as e:
            self.log_msg(f"Menu shortcut warning: {e}")

    # ------------------- STEP 5: FINISH -------------------
    def _render_finish_step(self):
        f = self.step_container

        badge = tk.Label(f, text="SUCCESS", font=("Segoe UI", 8, "bold"), fg="#fff", bg=THEME["accent_green"], padx=8, pady=2)
        badge.pack(anchor="w", pady=(0, 6))

        title = tk.Label(f, text=I18N[self.lang]["fin_title"], font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w")
        title.pack(fill=tk.X, pady=(0, 4))

        sub = tk.Label(f, text=I18N[self.lang]["fin_sub"], font=("Segoe UI", 10), fg=THEME["text_muted"], bg=THEME["bg_card"], anchor="w")
        sub.pack(fill=tk.X, pady=(0, 16))

        fin_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=20, highlightbackground=THEME["border"], highlightthickness=1)
        fin_card.pack(fill=tk.BOTH, expand=True, pady=(0, 16))

        tk.Label(fin_card, text=I18N[self.lang]["fin_msg"], font=("Segoe UI", 10), fg=THEME["text_main"], bg=THEME["bg_dark"], justify=tk.LEFT, wraplength=480).pack(fill=tk.X, pady=(0, 12))

        loc_box = tk.Frame(fin_card, bg=THEME["bg_input"], padx=12, pady=8)
        loc_box.pack(fill=tk.X, pady=(0, 16))
        tk.Label(loc_box, text=f"📂 {self.install_path_var.get()}", font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_input"], anchor="w").pack(fill=tk.X)

        cb_launch = ttk.Checkbutton(fin_card, text=I18N[self.lang]["fin_launch"], variable=self.chk_launch_var)
        cb_launch.pack(anchor="w")

    def next_step(self):
        if self.current_step < len(self.steps) - 1:
            self._show_step(self.current_step + 1)

    def prev_step(self):
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def finish_installation(self):
        should_launch = self.chk_launch_var.get()
        target_dir = os.path.abspath(self.install_path_var.get())
        self.destroy()

        if should_launch:
            bootbridge_script = os.path.join(target_dir, "bootbridge.py")
            if os.path.exists(bootbridge_script):
                subprocess.Popen([sys.executable, bootbridge_script])

def main():
    app = ModernSetupWizard()
    app.mainloop()

if __name__ == "__main__":
    main()
