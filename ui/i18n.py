"""
BootBridge i18n Translations Dictionary & Handler
"""

TRANSLATIONS = {
    "id": {
        "nav_title": "NAVIGATION",
        "nav_dashboard": "Dashboard & Drive",
        "nav_safety": "Proteksi & Safety",
        "nav_hardware": "Konfigurasi Hardware",
        "nav_guides": "Panduan & Shortcut",
        "nav_diagnostics": "Konsol Diagnostik",
        "nav_remote": "Remote PC & Desktop",
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
        "unmount_btn_done": "Partisi Unmounted (Aman)",
        "fix_ntfs_btn": "Reset Status NTFS / Fast Startup",
        "fix_ntfs_btn_done": "Status NTFS Clean",
        "enable_fast_btn": "Matikan Fast Startup (Default / Aman)",
        "enable_fast_btn_done": "Fast Startup Nonaktif (Aman)",

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
        "shortcut_title": "Fitur Canggih & Shortcut Layar VM (Fullscreen, Mouse, Keys, Copy-Paste)",
        "shortcut_markup": (
            "<b>Daftar Fitur &amp; Shortcut QEMU VM yang Bisa Kamu Gunakan:</b>\n\n"
            "• <b>Pop-up Petunjuk Shortcut:</b> Tekan <b><tt>Ctrl + Alt + H</tt></b> kapan saja untuk memunculkan panduan kontrol VM.\n"
            "• <b>Proteksi Jendela (Tanpa Tombol Close):</b> Jendela QEMU dirancang tanpa titlebar &amp; tombol close agar tidak sengaja mati saat digunakan.\n"
            "• <b>Tombol Logo Windows:</b> Penekanan tombol Logo Windows di keyboard langsung diarahkan ke Start Menu Windows VM.\n"
            "• <b>Toggle Fullscreen:</b> Tekan <b><tt>Ctrl + Alt + F</tt></b> di dalam jendela VM untuk masuk/keluar mode Layar Penuh.\n"
            "• <b>Shared Clipboard (Copy-Paste):</b> Gunakan <b><tt>Ctrl + C</tt></b> &amp; <b><tt>Ctrl + V</tt></b> untuk menyalin/merekat teks secara langsung antara Linux Host dan Windows VM.\n"
            "• <b>Lepas / Tangkap Mouse:</b> Tekan <b><tt>Ctrl + Alt + G</tt></b> jika kursor kaku atau ingin melepas kursor dari VM."
        ),
        "clipboard_card_title": "Cara Mengaktifkan Fitur Copy - Paste (Linux ↔ Windows VM)",
        "clipboard_markup": (
            "<b>Otomatisasi Driver Copy-Paste oleh BootBridge:</b>\n\n"
            "BootBridge sudah mengaktifkan jalur hardware serial <b><tt>qemu-vdagent</tt></b> dan <b>meng-embed drive USB virtual</b> secara otomatis di dalam Windows VM kamu!\n\n"
            "<b>Langkah Aktivasi (Tanpa Perlu Download Browser):</b>\n"
            "1. Jalankan VM Windows kamu via BootBridge.\n"
            "2. Buka <b>File Explorer</b> di dalam Windows VM -> buka <b>Drive Removable/USB (D: atau E:)</b>.\n"
            "3. Klik 2x file installer <b><tt>spice-guest-tools-latest.exe</tt></b> yang sudah disiapkan di drive tersebut.\n"
            "4. Selesai! Setelah install, fungsi Copy &amp; Paste (<b>Ctrl+C / Ctrl+V</b>) langsung aktif otomatis dua arah."
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
        "guide_dialog_title": "Petunjuk Cepat Kontrol & Shortcut VM",
        "guide_dialog_markup": (
            "<b>Tips Kontrol Virtual Machine (Emulator Style):</b>\n\n"
            "• <b>Toggle Fullscreen:</b> Tekan <b><tt>Ctrl + Alt + F</tt></b> untuk mode Layar Penuh.\n"
            "• <b>Kursor &amp; Keyboard:</b> Tekan <b><tt>Ctrl + Alt + G</tt></b> untuk melepas/menangkap kursor.\n"
            "• <b>Shared Copy-Paste:</b> Gunakan <b><tt>Ctrl + C</tt></b> &amp; <b><tt>Ctrl + V</tt></b> (setelah install SPICE Guest Tools di VM).\n"
            "• <b>Tampilkan Petunjuk Kapan Saja:</b> Tekan <b><tt>Ctrl + Alt + H</tt></b> untuk memunculkan petunjuk ini kembali.\n"
            "• <b>Proteksi Window:</b> Jendela VM tanpa tombol close. Matikan VM via Windows Shutdown atau tombol <b>Hentikan VM</b>."
        ),
        "dont_show_again": "Jangan tampilkan petunjuk ini lagi saat memulai VM",
        "btn_continue": "Lanjutkan Boot VM",
        "btn_cancel": "Batal",

        "remote_dep_title": "Komponen Remote Desktop Belum Terpasang",
        "remote_dep_msg": "Aplikasi membutuhkan komponen <b>freerdp2-x11</b> untuk meremote PC Windows.\nKlik tombol di bawah untuk memasang komponen secara otomatis:",
        "install_remote_dep_btn": "Pasang Komponen Remote Desktop (1-Klik)",
        "remote_scan_title": "Pindai Komputer Windows di Jaringan Wi-Fi / LAN (Otomatis)",
        "remote_scan_btn": "Pindai Jaringan Wi-Fi",
        "remote_scanning": "Memindai Jaringan...",
        "remote_scan_placeholder": "Klik 'Pindai Jaringan Wi-Fi' untuk menemukan PC Windows otomatis...",
        "remote_no_devices_found": "Tidak ada PC Windows RDP yang terdeteksi di jaringan lokal",
        "remote_select_detected": "-- Pilih Komputer Windows Terdeteksi --",
        "remote_card_title": "Konfigurasi Remote Desktop & Server Connection",
        "remote_proto": "Protokol Remote:",
        "remote_host": "IP / Host Target:",
        "remote_port": "Port Connection:",
        "remote_user": "Username (RDP):",
        "remote_pass": "Password Target:",
        "remote_options_title": "Pengaturan Performa & Layar Remote",
        "remote_fullscreen_chk": "Jalankan Remote Desktop dalam Mode Layar Penuh (Fullscreen)",
        "remote_clip_chk": "Aktifkan Shared Clipboard (Copy-Paste Dua Arah)",
        "remote_audio_chk": "Aktifkan Passthrough Suara / Audio (PulseAudio)",
        "remote_dynres_chk": "Aktifkan Penyesuaian Resolusi Otomatis (Dynamic Resolution)",
        "connect_remote_btn": "HUBUNGKAN KE REMOTE PC",
        "disconnect_remote_btn": "HENTIKAN KONEKSI REMOTE",
        "remote_guide_title": "Panduan Praktis Cara Meremote PC Windows (Untuk Orang Awam)",
        "remote_guide_markup": (
            "<b>Cara Mudah Mengakses Laptop / PC Windows Lain:</b>\n\n"
            "1. <b>Aktifkan Remote Desktop di PC Windows Target:</b>\n"
            "   Di PC Windows yang mau di-remote, buka <b>Settings</b> ➡️ <b>System</b> ➡️ <b>Remote Desktop</b> ➡️ Aktifkan tombol <b>Enable Remote Desktop</b>.\n\n"
            "2. <b>Pindai Otomatis di BootBridge:</b>\n"
            "   Klik tombol <b>'Pindai Jaringan Wi-Fi'</b> di atas. BootBridge akan otomatis menemukan PC Windows tersebut tanpa kamu harus mengetik nomor IP!\n\n"
            "3. <b>Masukkan Username &amp; Password:</b>\n"
            "   Isi Username dan Password login Windows target, lalu klik tombol biru <b>HUBUNGKAN KE REMOTE PC</b>. Selesai!"
        ),
    },
    "en": {
        "nav_title": "NAVIGATION",
        "nav_dashboard": "Dashboard & Drive",
        "nav_safety": "Safety & Mounts",
        "nav_hardware": "Resource Config",
        "nav_guides": "Help & Shortcuts",
        "nav_diagnostics": "Live Diagnostics",
        "nav_remote": "Remote PC & Desktop",
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
        "unmount_btn_done": "Partitions Unmounted (Safe)",
        "fix_ntfs_btn": "Reset NTFS Status / Fast Startup",
        "fix_ntfs_btn_done": "NTFS Status Clean",
        "enable_fast_btn": "Disable Fast Startup (Default / Safe)",
        "enable_fast_btn_done": "Fast Startup Disabled (Safe)",

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
        "shortcut_title": "VM Features & Screen Shortcuts (Fullscreen, Mouse, Keys, Copy-Paste)",
        "shortcut_markup": (
            "<b>Available QEMU VM Features &amp; Shortcuts:</b>\n\n"
            "• <b>Shortcut Guide Overlay:</b> Press <b><tt>Ctrl + Alt + H</tt></b> anytime to display the control guide dialog.\n"
            "• <b>Window Protection (No Close Button):</b> QEMU display window is framed without titlebar &amp; close button to prevent accidental VM termination.\n"
            "• <b>Windows Logo Key:</b> Pressing the Windows key is captured directly by Windows VM Start Menu.\n"
            "• <b>Toggle Fullscreen:</b> Press <b><tt>Ctrl + Alt + F</tt></b> inside VM window to toggle Fullscreen mode.\n"
            "• <b>Shared Clipboard (Copy-Paste):</b> Use <b><tt>Ctrl + C</tt></b> &amp; <b><tt>Ctrl + V</tt></b> to copy/paste text seamlessly between Linux Host and Windows VM.\n"
            "• <b>Release / Grab Mouse:</b> Press <b><tt>Ctrl + Alt + G</tt></b> to ungrab/release mouse pointer from VM."
        ),
        "clipboard_card_title": "How to Enable Shared Clipboard (Linux ↔ Windows VM)",
        "clipboard_markup": (
            "<b>Automatic Copy-Paste Driver Integration by BootBridge:</b>\n\n"
            "BootBridge has automatically enabled <b><tt>qemu-vdagent</tt></b> hardware channels and <b>auto-mounted a virtual USB driver disk</b> inside your Windows VM!\n\n"
            "<b>Activation Steps (No Browser Download Needed):</b>\n"
            "1. Launch your Windows VM via BootBridge.\n"
            "2. Open <b>File Explorer</b> inside Windows VM -> open the <b>Removable USB Drive (D: or E:)</b>.\n"
            "3. Double-click <b><tt>spice-guest-tools-latest.exe</tt></b> which BootBridge provided automatically on that drive.\n"
            "4. Done! Copy &amp; Paste (<b>Ctrl+C / Ctrl+V</b>) is now active bidirectionally."
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
        "sys_info_title": "Host Specifications & Hypervisor Info",
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
        "guide_dialog_title": "Quick VM Controls & Shortcuts Guide",
        "guide_dialog_markup": (
            "<b>Virtual Machine Control Tips (Emulator Style):</b>\n\n"
            "• <b>Toggle Fullscreen:</b> Press <b><tt>Ctrl + Alt + F</tt></b> for full-screen mode.\n"
            "• <b>Mouse &amp; Keyboard:</b> Press <b><tt>Ctrl + Alt + G</tt></b> to release/grab mouse focus.\n"
            "• <b>Shared Copy-Paste:</b> Use <b><tt>Ctrl + C</tt></b> &amp; <b><tt>Ctrl + V</tt></b> (after installing SPICE Guest Tools in VM).\n"
            "• <b>Show Guide Anytime:</b> Press <b><tt>Ctrl + Alt + H</tt></b> to open this guide dialog overlay anytime.\n"
            "• <b>Window Guard:</b> Frameless VM display without close button. Shut down via Windows or <b>Stop VM</b> button."
        ),
        "dont_show_again": "Don't show this shortcut guide again when launching VM",
        "btn_continue": "Continue Boot VM",
        "btn_cancel": "Cancel",

        "remote_dep_title": "Remote Desktop Components Missing",
        "remote_dep_msg": "The application requires the <b>freerdp2-x11</b> package to connect to remote Windows PCs.\nClick the button below to install components automatically:",
        "install_remote_dep_btn": "Install Remote Desktop Components (1-Click)",
        "remote_scan_title": "Auto-Scan Windows PCs on Wi-Fi / LAN Network",
        "remote_scan_btn": "Scan Wi-Fi Network",
        "remote_scanning": "Scanning Network...",
        "remote_scan_placeholder": "Click 'Scan Wi-Fi Network' to discover Windows PCs automatically...",
        "remote_no_devices_found": "No active RDP Windows PCs detected on local network",
        "remote_select_detected": "-- Select Detected Windows PC --",
        "remote_card_title": "Remote Desktop & Server Connection Configuration",
        "remote_proto": "Remote Protocol:",
        "remote_host": "Target IP / Host:",
        "remote_port": "Connection Port:",
        "remote_user": "Username (RDP):",
        "remote_pass": "Target Password:",
        "remote_options_title": "Remote Performance & Display Settings",
        "remote_fullscreen_chk": "Launch Remote Desktop in Fullscreen Mode",
        "remote_clip_chk": "Enable Shared Clipboard (Bidirectional Copy-Paste)",
        "remote_audio_chk": "Enable Audio / Sound Passthrough (PulseAudio)",
        "remote_dynres_chk": "Enable Automatic Resolution Scaling (Dynamic Resolution)",
        "connect_remote_btn": "CONNECT TO REMOTE PC",
        "disconnect_remote_btn": "DISCONNECT REMOTE SESSION",
        "remote_guide_title": "Beginner's Guide to Remote Windows PCs",
        "remote_guide_markup": (
            "<b>Easy 3-Step Remote Desktop Setup:</b>\n\n"
            "1. <b>Enable Remote Desktop on Windows:</b>\n"
            "   On the target Windows PC, open <b>Settings</b> ➡️ <b>System</b> ➡️ <b>Remote Desktop</b> ➡️ turn ON <b>Enable Remote Desktop</b>.\n\n"
            "2. <b>Auto-Scan in BootBridge:</b>\n"
            "   Click <b>'Scan Wi-Fi Network'</b> above. BootBridge automatically discovers the Windows PC without needing to type IP addresses!\n\n"
            "3. <b>Enter Credentials &amp; Connect:</b>\n"
            "   Enter target Windows Username &amp; Password, then click the blue <b>CONNECT TO REMOTE PC</b> button. Done!"
        ),
    }
}

def tr(key, lang="id", **kwargs):
    """Translates a translation key into the requested language with optional string formatting."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["id"])
    text = lang_dict.get(key, TRANSLATIONS["id"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
