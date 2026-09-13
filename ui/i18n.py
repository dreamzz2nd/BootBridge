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
        "enable_fast_btn": "Aktifkan Fast Startup",
        "enable_fast_btn_done": "Fast Startup Aktif",

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
        "unmount_btn_done": "Partitions Unmounted (Safe)",
        "fix_ntfs_btn": "Reset NTFS Status / Fast Startup",
        "fix_ntfs_btn_done": "NTFS Status Clean",
        "enable_fast_btn": "Enable Fast Startup",
        "enable_fast_btn_done": "Fast Startup Active",

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

def tr(key, lang="id", **kwargs):
    """Translates a translation key into the requested language with optional string formatting."""
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["id"])
    text = lang_dict.get(key, TRANSLATIONS["id"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text
