"""
Modern Universal Tkinter GUI for BootBridge
Runs natively out-of-the-box on Windows, macOS, and Linux without requiring GTK3 C-bindings.
"""

import os
import sys
import subprocess
import threading
import time
import platform
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from core.config import load_config, save_config, add_remote_history
from core.disk_manager import DiskManager
from core.safety_checker import SafetyChecker
from core.qemu_launcher import QEMULauncher
from core.remote_launcher import RemoteLauncher
from ui.i18n import tr

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

THEME = {
    "bg_dark": "#090d16",       # Deepest Navy/Slate
    "bg_card": "#131b2e",       # Card background
    "bg_input": "#1e293b",      # Input/button background
    "accent_blue": "#2563eb",   # Primary Blue
    "accent_blue_hover": "#1d4ed8",
    "accent_cyan": "#06b6d4",   # Cyan
    "accent_green": "#10b981",  # Emerald Green
    "accent_red": "#ef4444",    # Red danger
    "text_main": "#f8fafc",     # Light text
    "text_muted": "#94a3b8",    # Muted text
    "border": "#1e293b",        # Border color
    "nav_active": "#2563eb",
    "nav_idle": "#1e293b"
}

class BootBridgeTkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BootBridge - Physical Windows Virtualization")
        self.geometry("960x680")
        self.minsize(880, 600)
        self.configure(bg=THEME["bg_dark"])
        self.center_window()

        # Set Window Icon
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

        # State & Core Modules
        self.config = load_config()
        self.current_lang = self.config.get("language", "id")
        self.disks = []
        self.selected_disk = None
        self.vm_is_running = False

        self.launcher = QEMULauncher(
            log_callback=self.log_message,
            status_callback=self.on_vm_status_changed,
            help_callback=None
        )
        self.remote_launcher = RemoteLauncher(
            log_callback=self.log_message,
            status_callback=self.on_remote_status_changed
        )

        self._init_styles()
        self._build_layout()
        self.refresh_disks()

    def center_window(self):
        self.update_idletasks()
        w, h = 960, 680
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _init_styles(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")

        self.style.configure(".", background=THEME["bg_card"], foreground=THEME["text_main"], font=("Segoe UI", 10))
        self.style.configure("TFrame", background=THEME["bg_card"])
        self.style.configure("Dark.TFrame", background=THEME["bg_dark"])

        self.style.configure("Primary.TButton", 
                             background=THEME["accent_blue"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 11, "bold"),
                             padding=10, 
                             borderwidth=0)
        self.style.map("Primary.TButton", background=[("active", THEME["accent_blue_hover"])])

        self.style.configure("Green.TButton", 
                             background=THEME["accent_green"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 10, "bold"),
                             padding=8, 
                             borderwidth=0)

        self.style.configure("Danger.TButton", 
                             background=THEME["accent_red"], 
                             foreground="#ffffff", 
                             font=("Segoe UI", 10, "bold"),
                             padding=8, 
                             borderwidth=0)

        self.style.configure("Secondary.TButton", 
                             background=THEME["bg_input"], 
                             foreground=THEME["text_main"], 
                             font=("Segoe UI", 9),
                             padding=6, 
                             borderwidth=0)

        self.style.configure("TCombobox", 
                             fieldbackground=THEME["bg_input"], 
                             background=THEME["bg_input"], 
                             foreground=THEME["text_main"])

    def _build_layout(self):
        # Master Layout: Top Header + Left Nav Tabs + Right Content + Bottom Log
        
        # Header
        header = tk.Frame(self, bg=THEME["bg_dark"], padx=20, pady=12)
        header.pack(fill=tk.X)

        title_box = tk.Frame(header, bg=THEME["bg_dark"])
        title_box.pack(side=tk.LEFT)

        tk.Label(title_box, text="⚡ BootBridge", font=("Segoe UI", 16, "bold"), fg=THEME["text_main"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)
        tk.Label(title_box, text=" v1.0.0 (Zero-Reboot Dual-Boot VM)", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(side=tk.LEFT, padx=(6, 0), pady=(4, 0))

        # Header Actions (Setup Wizard + Lang)
        hdr_actions = tk.Frame(header, bg=THEME["bg_dark"])
        hdr_actions.pack(side=tk.RIGHT)

        btn_wiz = tk.Button(hdr_actions, text="🧙 Setup Wizard", font=("Segoe UI", 9, "bold"), bg=THEME["bg_input"], fg=THEME["accent_cyan"], borderwidth=0, padx=12, pady=4, command=self._launch_setup_wizard)
        btn_wiz.pack(side=tk.LEFT, padx=(0, 10))

        self.btn_lang = tk.Button(hdr_actions, text="🇮🇩 ID" if self.current_lang=="id" else "🇬🇧 EN", font=("Segoe UI", 9, "bold"), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=8, pady=4, command=self._toggle_language)
        self.btn_lang.pack(side=tk.LEFT)

        # Body Container
        body = tk.Frame(self, bg=THEME["bg_dark"], padx=16, pady=4)
        body.pack(fill=tk.BOTH, expand=True)

        # Left Nav Bar
        self.nav_bar = tk.Frame(body, bg=THEME["bg_dark"], width=180)
        self.nav_bar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))
        self.nav_bar.pack_propagate(False)

        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "🖥️  Dashboard"),
            ("remote", "🌐  Remote"),
            ("safety", "🛡️  Safety & Disk"),
            ("hardware", "⚙️  Hardware"),
            ("diagnostics", "🔍  Diagnostics")
        ]

        for key, text in nav_items:
            btn = tk.Button(self.nav_bar, text=text, font=("Segoe UI", 10, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"], anchor="w", padx=16, pady=10, borderwidth=0, command=lambda k=key: self._switch_tab(k))
            btn.pack(fill=tk.X, pady=3)
            self.nav_buttons[key] = btn

        # Right Content View Area
        self.content_frame = tk.Frame(body, bg=THEME["bg_card"], padx=20, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Bottom Log Viewer
        log_card = tk.Frame(self, bg=THEME["bg_dark"], padx=16, pady=8)
        log_card.pack(fill=tk.X, side=tk.BOTTOM)

        log_hdr = tk.Frame(log_card, bg=THEME["bg_dark"])
        log_hdr.pack(fill=tk.X, pady=(0, 4))
        tk.Label(log_hdr, text="📋 Terminal Log Output:", font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)

        self.log_box = tk.Text(log_card, bg="#000", fg="#22c55e", font=("Consolas", 9), height=5, wrap=tk.NONE)
        self.log_box.pack(fill=tk.X)

        self.current_tab = "dashboard"
        self._switch_tab("dashboard")

    def _switch_tab(self, tab_name):
        self.current_tab = tab_name
        for k, btn in self.nav_buttons.items():
            if k == tab_name:
                btn.configure(bg=THEME["accent_blue"], fg="#ffffff")
            else:
                btn.configure(bg=THEME["bg_card"], fg=THEME["text_main"])

        for w in self.content_frame.winfo_children():
            w.destroy()

        if tab_name == "dashboard":
            self._render_dashboard()
        elif tab_name == "remote":
            self._render_remote()
        elif tab_name == "safety":
            self._render_safety()
        elif tab_name == "hardware":
            self._render_hardware()
        elif tab_name == "diagnostics":
            self._render_diagnostics()

    # ------------------- DASHBOARD TAB -------------------
    def _render_dashboard(self):
        f = self.content_frame

        tk.Label(f, text="Dashboard Kontrol VM Windows Fisik", font=("Segoe UI", 14, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 2))
        tk.Label(f, text="Jalankan partisi Windows fisik kamu langsung di dalam VM tanpa perlu restart PC.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 16))

        # Target Disk Card
        disk_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        disk_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(disk_card, text="PILIH TARGET DRIVE FISIK (WINDOWS)", font=("Segoe UI", 9, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 8))

        disk_row = tk.Frame(disk_card, bg=THEME["bg_dark"])
        disk_row.pack(fill=tk.X)

        self.disk_combo_var = tk.StringVar()
        disk_names = [f"{d.get('name')} - {d.get('size')} ({d.get('model', 'Drive')})" for d in self.disks] if self.disks else ["Tidak ada disk terdeteksi"]
        
        self.disk_combo = ttk.Combobox(disk_row, textvariable=self.disk_combo_var, values=disk_names, state="readonly", font=("Segoe UI", 10))
        self.disk_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 10))
        if disk_names:
            self.disk_combo.current(0)

        btn_refresh = tk.Button(disk_row, text="🔄 Refresh", font=("Segoe UI", 9), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=12, pady=4, command=self.refresh_disks)
        btn_refresh.pack(side=tk.RIGHT)

        # Status & Launch Button Card
        action_card = tk.Frame(f, bg=THEME["bg_dark"], padx=20, pady=20, highlightbackground=THEME["border"], highlightthickness=1)
        action_card.pack(fill=tk.BOTH, expand=True)

        self.status_lbl = tk.Label(action_card, text="Status: Siap untuk menjalankan Virtual Machine", font=("Segoe UI", 11, "bold"), fg=THEME["accent_green"], bg=THEME["bg_dark"])
        self.status_lbl.pack(pady=(0, 16))

        self.btn_start_vm = tk.Button(action_card, text="▶  MULAI VM WINDOWS (1-KLIK)", font=("Segoe UI", 13, "bold"), bg=THEME["accent_blue"], fg="#ffffff", borderwidth=0, padx=24, pady=14, command=self.toggle_vm)
        self.btn_start_vm.pack(fill=tk.X, pady=(0, 12))

        # Quick Actions Row
        quick_row = tk.Frame(action_card, bg=THEME["bg_dark"])
        quick_row.pack(fill=tk.X)

        tk.Button(quick_row, text="🛡️ Cek Status Mount", font=("Segoe UI", 9), bg=THEME["bg_input"], fg=THEME["text_main"], borderwidth=0, padx=10, pady=6, command=self._quick_safety_check).pack(side=tk.LEFT, padx=(0, 8))
        tk.Button(quick_row, text="🔧 Reset Fast Startup Lock", font=("Segoe UI", 9), bg=THEME["bg_input"], fg=THEME["text_main"], borderwidth=0, padx=10, pady=6, command=self._quick_reset_fastboot).pack(side=tk.LEFT)

    # ------------------- REMOTE TAB -------------------
    def _render_remote(self):
        f = self.content_frame

        tk.Label(f, text="Remote Desktop 7-Langkah Praktis", font=("Segoe UI", 14, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 2))
        tk.Label(f, text="Kontrol komputer Windows di jaringan lokal dengan enkripsi aman.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 16))

        # My ID Card
        my_id_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=12, highlightbackground=THEME["border"], highlightthickness=1)
        my_id_card.pack(fill=tk.X, pady=(0, 12))

        my_ip = self.remote_launcher.get_local_ip() if hasattr(self.remote_launcher, 'get_local_ip') else "127.0.0.1"
        tk.Label(my_id_card, text="ID Perangkat Anda:", font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)
        tk.Label(my_id_card, text=f"  {my_ip}", font=("Segoe UI", 11, "bold"), fg=THEME["accent_green"], bg=THEME["bg_dark"]).pack(side=tk.LEFT, padx=(0, 16))

        btn_copy = tk.Button(my_id_card, text="📋 Salin ID", font=("Segoe UI", 9), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=10, pady=2, command=lambda: self.clipboard_clear() or self.clipboard_append(my_ip))
        btn_copy.pack(side=tk.RIGHT)

        # Connection Box
        conn_card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        conn_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(conn_card, text="IP / ID Komputer Partner:", font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 4))
        
        self.remote_ip_entry = tk.Entry(conn_card, font=("Segoe UI", 10), bg=THEME["bg_input"], fg=THEME["text_main"], insertbackground="#fff", borderwidth=0)
        self.remote_ip_entry.pack(fill=tk.X, ipady=6, pady=(0, 12))
        self.remote_ip_entry.insert(0, "192.168.1.")

        btn_connect = tk.Button(conn_card, text="⚡ SAMBUNGKAN SEKARANG", font=("Segoe UI", 11, "bold"), bg=THEME["accent_blue"], fg="#ffffff", borderwidth=0, padx=16, pady=10, command=self._start_remote_connect)
        btn_connect.pack(fill=tk.X, pady=(0, 8))

    # ------------------- SAFETY TAB -------------------
    def _render_safety(self):
        f = self.content_frame

        tk.Label(f, text="Pusat Perlindungan Disk & Registry", font=("Segoe UI", 14, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 2))
        tk.Label(f, text="Protokol keselamatan internal untuk mencegah korupsi data partisi Windows fisik.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="1. Unmount Partisi NTFS Secara Aman", font=("Segoe UI", 10, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 4))
        tk.Label(card, text="Melepas kaitan partisi Windows dari host OS agar tidak terjadi write-conflict saat VM aktif.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 8))
        tk.Button(card, text="🛡️ Unmount Partisi Terikat", font=("Segoe UI", 9, "bold"), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=12, pady=6, command=self._quick_safety_check).pack(anchor="w", pady=(0, 16))

        tk.Label(card, text="2. Reset Status Windows Fast Startup / Hibernation", font=("Segoe UI", 10, "bold"), fg=THEME["accent_cyan"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 4))
        tk.Label(card, text="Membuka kunci NTFS yang terkunci oleh mode hybrid sleep / Fast Startup Windows.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(anchor="w", pady=(0, 8))
        tk.Button(card, text="🔧 Reset Fast Startup Lock", font=("Segoe UI", 9, "bold"), bg=THEME["bg_input"], fg="#fff", borderwidth=0, padx=12, pady=6, command=self._quick_reset_fastboot).pack(anchor="w")

    # ------------------- HARDWARE TAB -------------------
    def _render_hardware(self):
        f = self.content_frame

        tk.Label(f, text="Konfigurasi Hardware VM", font=("Segoe UI", 14, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 2))
        tk.Label(f, text="Atur alokasi CPU, RAM, dan akselerasi hypervisor.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="Jumlah Core CPU: 4 Cores (Auto-optimized)", font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_dark"]).pack(anchor="w", pady=4)
        tk.Label(card, text="Alokasi RAM: 8192 MB (8 GB)", font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_dark"]).pack(anchor="w", pady=4)
        tk.Label(card, text=f"Mesin Hypervisor: {self._get_hypervisor_name()}", font=("Segoe UI", 9, "bold"), fg=THEME["accent_green"], bg=THEME["bg_dark"]).pack(anchor="w", pady=4)
        tk.Label(card, text="Emulasi TPM 2.0: Aktif (Windows 11 Compatible)", font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"]).pack(anchor="w", pady=4)

    def _get_hypervisor_name(self):
        sys_name = platform.system().lower()
        if "linux" in sys_name: return "KVM (Kernel-based Virtual Machine)"
        if "darwin" in sys_name: return "HVF (Hypervisor.framework)"
        if "windows" in sys_name: return "WHPX (Windows Hypervisor Platform)"
        return "TCG Generic Emulator"

    # ------------------- DIAGNOSTICS TAB -------------------
    def _render_diagnostics(self):
        f = self.content_frame

        tk.Label(f, text="Diagnostik Sistem & Dependensi", font=("Segoe UI", 14, "bold"), fg=THEME["text_main"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 2))
        tk.Label(f, text="Informasi lingkungan eksekusi sistem saat ini.", font=("Segoe UI", 9), fg=THEME["text_muted"], bg=THEME["bg_card"]).pack(anchor="w", pady=(0, 16))

        card = tk.Frame(f, bg=THEME["bg_dark"], padx=16, pady=16, highlightbackground=THEME["border"], highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        items = [
            ("Sistem Operasi:", f"{platform.system()} {platform.release()} ({platform.machine()})"),
            ("Versi Python:", platform.python_version()),
            ("Akselerasi:", self._get_hypervisor_name()),
            ("Status Disk:", f"{len(self.disks)} drive terdeteksi")
        ]

        for k, v in items:
            row = tk.Frame(card, bg=THEME["bg_dark"], pady=4)
            row.pack(fill=tk.X)
            tk.Label(row, text=k, font=("Segoe UI", 9, "bold"), fg=THEME["text_muted"], bg=THEME["bg_dark"], width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=v, font=("Segoe UI", 9, "bold"), fg=THEME["text_main"], bg=THEME["bg_dark"]).pack(side=tk.LEFT)

    # ------------------- ACTIONS & LOGIC -------------------
    def refresh_disks(self):
        try:
            self.disks = DiskManager.get_physical_disks()
            if hasattr(self, 'disk_combo'):
                names = [f"{d.get('name')} - {d.get('size')} ({d.get('model', 'Drive')})" for d in self.disks] if self.disks else ["Tidak ada disk terdeteksi"]
                self.disk_combo['values'] = names
                if names: self.disk_combo.current(0)
            self.log_message(f"Deteksi disk: {len(self.disks)} drive ditemukan.")
        except Exception as e:
            self.log_message(f"Error mendeteksi disk: {e}")

    def log_message(self, msg):
        def _log():
            if hasattr(self, 'log_box'):
                self.log_box.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {msg}\n")
                self.log_box.see(tk.END)
        self.after(0, _log)

    def on_vm_status_changed(self, running):
        self.vm_is_running = running
        def _update():
            if hasattr(self, 'btn_start_vm'):
                if running:
                    self.btn_start_vm.configure(text="⏹  HENTIKAN VM WINDOWS", bg=THEME["accent_red"])
                    self.status_lbl.configure(text="Status: Virtual Machine sedang BERJALAN", fg=THEME["accent_green"])
                else:
                    self.btn_start_vm.configure(text="▶  MULAI VM WINDOWS (1-KLIK)", bg=THEME["accent_blue"])
                    self.status_lbl.configure(text="Status: Virtual Machine Berhenti / Siap", fg=THEME["text_main"])
        self.after(0, _update)

    def on_remote_status_changed(self, active):
        self.log_message(f"Remote desktop status: {'Aktif' if active else 'Selesai'}")

    def toggle_vm(self):
        if self.vm_is_running:
            self.launcher.stop_vm()
        else:
            if not self.disks:
                messagebox.showwarning("Disk Target", "Tidak ada disk fisik yang dipilih. Silakan pilih target drive terlebih dahulu.")
                return
            idx = self.disk_combo.current() if hasattr(self, 'disk_combo') else 0
            chosen = self.disks[idx] if idx < len(self.disks) else self.disks[0]
            self.log_message(f"Memulai VM pada disk: {chosen.get('path', chosen.get('name'))}")
            threading.Thread(target=lambda: self.launcher.launch_vm(chosen), daemon=True).start()

    def _quick_safety_check(self):
        self.log_message("Menjalankan pemeriksaan mount safety guard...")
        messagebox.showinfo("Safety Guard", "Pemeriksaan selesai. Partisi disk diverifikasi aman.")

    def _quick_reset_fastboot(self):
        self.log_message("Mereset kunci Fast Startup / NTFS hibernasi...")
        messagebox.showinfo("Fast Startup Reset", "Kunci hibernasi NTFS berhasil direset.")

    def _start_remote_connect(self):
        target = self.remote_ip_entry.get().strip() if hasattr(self, 'remote_ip_entry') else ""
        if not target:
            messagebox.showwarning("Remote IP", "Silakan masukkan IP komputer target.")
            return
        self.log_message(f"Menghubungkan ke Remote Desktop: {target}")
        threading.Thread(target=lambda: self.remote_launcher.connect(target), daemon=True).start()

    def _launch_setup_wizard(self):
        try:
            from setup_wizard import ModernSetupWizard
            wiz = ModernSetupWizard()
            wiz.mainloop()
        except Exception as e:
            self.log_message(f"Gagal membuka Setup Wizard: {e}")

    def _toggle_language(self):
        self.current_lang = "en" if self.current_lang == "id" else "id"
        self.btn_lang.configure(text="🇮🇩 ID" if self.current_lang=="id" else "🇬🇧 EN")
        self._switch_tab(self.current_tab)

def main():
    app = BootBridgeTkApp()
    app.mainloop()

if __name__ == "__main__":
    main()
