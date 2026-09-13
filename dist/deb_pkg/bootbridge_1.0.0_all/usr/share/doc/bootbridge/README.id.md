<div align="center">

<img src="assets/bootbridge.png" width="128" height="128" alt="BootBridge Logo" />

# BootBridge

### *Aplikasi Virtualisasi Dual-Boot Fisik yang Ringan, Aman & Zero-Reboot*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![GUI Framework](https://img.shields.io/badge/GUI-GTK3%20%7C%20Tkinter-4B8BBE.svg?logo=gnome&logoColor=white)](https://www.gtk.org/)
[![Hypervisor Engines](https://img.shields.io/badge/Hypervisor-KVM%20%7C%20HVF%20%7C%20WHPX-FF6600.svg?logo=qemu&logoColor=white)](https://www.qemu.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)](https://github.com/dreamzz2nd/BootBridge)

<p align="center">
  <b>Bahasa / Languages:</b> <a href="README.md">English</a> | <b><a href="README.id.md">Bahasa Indonesia</a></b>
</p>

<p align="center">
  <a href="https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/BootBridge-v1.0.0-Windows-Setup.exe">
    <img src="https://img.shields.io/badge/Unduh-Windows%20(.EXE)-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Unduh Windows EXE" />
  </a>
  <a href="https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/BootBridge-v1.0.0-macOS.dmg">
    <img src="https://img.shields.io/badge/Unduh-macOS%20(.DMG)-000000?style=for-the-badge&logo=apple&logoColor=white" alt="Unduh macOS DMG" />
  </a>
  <a href="https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/bootbridge_1.0.0_all.deb">
    <img src="https://img.shields.io/badge/Unduh-Linux%20(.DEB)-FCC624?style=for-the-badge&logo=linux&logoColor=black" alt="Unduh Linux DEB" />
  </a>
  <a href="https://github.com/dreamzz2nd/BootBridge/releases/tag/v1.0.0">
    <img src="https://img.shields.io/badge/Rilis-v1.0.0%20(Semua%20Paket)-brightgreen?style=for-the-badge&logo=github" alt="GitHub Release v1.0.0" />
  </a>
  <a href="https://ko-fi.com/dreamzz2nd">
    <img src="https://img.shields.io/badge/Dukung-Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black" alt="Buy Me A Coffee" />
  </a>
</p>

<p align="center">
  <b>🌐 <a href="web/index.html">Halaman Unduh Cerdas (Smart OS Auto-Detect)</a></b> — Otomatis mendeteksi sistem operasi Anda dan memberikan paket installer yang tepat (.exe / .dmg / .deb).
</p>

<p align="center">
  <b>BootBridge</b> adalah aplikasi desktop khusus yang dirancang untuk menjalankan sistem operasi Windows dual-boot fisik kamu secara aman di dalam Virtual Machine (QEMU dengan akselerasi hardware native) langsung dari desktop—<b>tanpa perlu merestart (reboot) komputer kamu</b>.
</p>

[Fitur Utama](#fitur-utama) •
[Dukungan Lintas Platform](#dukungan-lintas-platform) •
[Panduan Instalasi Multi-Platform](#panduan-instalasi-multi-platform) •
[Setup Wizard](#setup-wizard-modern-5-langkah) •
[Remote Desktop](#fitur-remote-desktop-sederhana) •
[Matriks Perbandingan](#matriks-perbandingan) •
[Troubleshooting](#troubleshooting--faq)

</div>

---

## Daftar Isi

- [Gambaran Umum](#gambaran-umum)
- [Fitur Utama](#fitur-utama)
- [Dukungan Lintas Platform](#dukungan-lintas-platform)
- [Panduan Instalasi Multi-Platform](#panduan-instalasi-multi-platform)
  - [1. Microsoft Windows (.exe)](#1-microsoft-windows-exe)
  - [2. Apple macOS (.dmg)](#2-apple-macos-dmg)
  - [3. Linux (.deb & Tarball)](#3-linux-deb--tarball)
  - [4. Skrip Terminal Otomatis 1-Baris](#4-skrip-terminal-otomatis-1-baris)
- [Setup Wizard Modern (5-Langkah)](#setup-wizard-modern-5-langkah)
- [Fitur Remote Desktop Sederhana](#fitur-remote-desktop-sederhana)
- [Matriks Perbandingan](#matriks-perbandingan)
- [Arsitektur Sistem](#arsitektur-sistem)
- [Persyaratan Sistem](#persyaratan-sistem)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Troubleshooting & FAQ](#troubleshooting--faq)
- [Pintasan Keyboard (Shortcuts)](#pintasan-keyboard-shortcuts)
- [Kontribusi & Lisensi](#kontribusi--lisensi)

---

## Gambaran Umum

Secara tradisional, pengguna dual-boot harus mematikan total sistem operasi mereka dan merestart komputer setiap kali ingin mengakses instalasi Windows fisik. **BootBridge** mengeliminasi proses perebutan restart ini dengan memanfaatkan **akselerasi hypervisor hardware native** dan **passthrough block device fisik QEMU**.

Dengan BootBridge, partisi Windows fisik kamu akan di-boot secara native di dalam jendela VM berkecepatan tinggi langsung di atas desktop kamu. Kamu tetap memiliki akses penuh ke seluruh file Windows fisik, game, dan aplikasi yang sudah terinstall, sambil menjalankan sistem operasi utama secara bersamaan.

---

## Fitur Utama

- ⚡ **Zero-Reboot Dual Booting**: Jalankan drive Windows fisik kamu di dalam sistem operasi utama dengan kecepatan mendekati bare-metal 1:1.
- 🌐 **Dukungan Lintas Platform & Paket Native**:
  - **Windows**: Installer `.exe` (Inno Setup) & Standalone executable.
  - **macOS**: Disk Image `.dmg` dengan integrasi `/Applications` (Intel & Apple Silicon M1-M4).
  - **Linux**: Paket Debian `.deb` dengan integrasi sistem `/usr/bin/bootbridge` & menu aplikasi.
- 🧙 **Setup Wizard Visual 5-Langkah**: Panduan instalasi interaktif untuk cek kesiapan hypervisor, pemilihan direktori, pembuatan shortcut, dan instalasi dependensi.
- 🛡️ **Mount Safety Guard**: Protokol perlindungan internal yang memverifikasi status mount disk, memberi peringatan terhadap akses partisi terbagi, dan melepas (unmount) drive NTFS terikat secara aman untuk mencegah kerusakan data.
- 🔧 **Fast Startup & Modifier Registry Offline**: Pengubah registry offline satu-klik untuk mengatur status Fast Startup Windows (`HiberbootEnabled = 1`) tanpa merusak filesystem.
- 📋 **Shared Clipboard Dua Arah**: Integrasi `qemu-vdagent` internal untuk copy-paste teks (`Ctrl+C` / `Ctrl+V`) dua arah antara host dan VM Windows.
- 🖥️ **Fitur Remote Desktop Sederhana**: Fitur koneksi remote desktop 7-langkah intuitif dengan ID perangkat unik otomatis, tombol salin IP 1-klik, dan pemindai Wi-Fi instan.
- 🪶 **100% Gratis & Sangat Ringan**: Penggunaan RAM hanya ~30–50 MB, 0% CPU idle footprint. Tanpa runtime web/Electron yang berat.

---

## Dukungan Lintas Platform

BootBridge dirancang untuk berjalan lancar di semua sistem operasi desktop utama dengan akselerasi hardware native:

| Sistem Operasi | Format Installer | Mesin Hypervisor | Antarmuka Penyimpanan | Remote Desktop Client |
| :--- | :--- | :--- | :--- | :--- |
| **Windows** (10 / 11) | **`.exe`** (Setup Wizard) | **WHPX** (`-accel whpx`) | `\\.\PhysicalDrive*` | Bawaan Native `mstsc.exe` |
| **macOS** (Intel / M1–M4) | **`.dmg`** (Disk Image) | **HVF** (`-accel hvf`) | `/dev/disk*` | `freerdp` / `remote-viewer` |
| **Linux** (Debian, Ubuntu, Mint, Arch, Fedora) | **`.deb`** / **`.tar.gz`** | **KVM** (`-accel kvm`) | `/dev/nvme*` atau `/dev/sd*` | `xfreerdp` / `spicy` |

---

## Panduan Instalasi Multi-Platform

### 1. Microsoft Windows (`.exe`)

1. Unduh **[BootBridge-v1.0.0-Windows-Setup.exe](https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/BootBridge-v1.0.0-Windows-Setup.exe)**.
2. Klik 2x pada file `.exe` untuk memulai Setup Wizard.
3. Ikuti petunjuk wizard untuk memilih lokasi instalasi dan membuat shortcut di Desktop / Start Menu.
4. Atau jalankan `bootbridge_installer.bat` dari paket ZIP portabel.

---

### 2. Apple macOS (`.dmg`)

1. Unduh **[BootBridge-v1.0.0-macOS.dmg](https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/BootBridge-v1.0.0-macOS.dmg)**.
2. Klik 2x file `.dmg` untuk membukanya.
3. Tarik ikon **BootBridge.app** ke folder **Applications**.
4. Buka BootBridge dari Launchpad atau folder Applications.

---

### 3. Linux (`.deb` & Tarball)

#### Opsi A: Menggunakan Paket Debian (.deb)
```bash
# Unduh paket .deb
wget https://github.com/dreamzz2nd/BootBridge/releases/download/v1.0.0/bootbridge_1.0.0_all.deb

# Pasang paket beserta dependensinya
sudo apt install ./bootbridge_1.0.0_all.deb
```

#### Opsi B: Menggunakan Setup Wizard GUI
```bash
python3 setup_wizard.py
```

---

### 4. Skrip Terminal Otomatis 1-Baris

Buka terminal dan jalankan 1 perintah berikut:

```bash
git clone https://github.com/dreamzz2nd/BootBridge.git && cd BootBridge && ./install.sh
```

---

## Setup Wizard Modern (5-Langkah)

BootBridge dilengkapi dengan **Setup Wizard Multi-Step** modern (`setup_wizard.py`) yang dapat berjalan langsung tanpa dependensi eksternal yang berat:

1. **Langkah 1 (Sambutan & Bahasa)**: Pilihan bahasa (Bahasa Indonesia 🇮🇩 / English 🇬🇧) dan overview fitur.
2. **Langkah 2 (Cek Kesiapan Sistem)**: Deteksi otomatis akselerasi hardware (KVM, WHPX, HVF), QEMU, dan Python.
3. **Langkah 3 (Opsi & Folder Tujuan)**: Pemilihan folder instalasi, shortcut Desktop, Start Menu, dan PATH.
4. **Langkah 4 (Proses Instalasi)**: Real-time progress bar dan expandable terminal logs.
5. **Langkah 5 (Selesai)**: Ringkasan instalasi sukses dan opsi langsung menjalankan aplikasi.

```bash
# Jalankan wizard kapan saja:
python setup_wizard.py
```

---

## Fitur Remote Desktop Sederhana

BootBridge dilengkapi dengan fitur koneksi Remote Desktop 7-langkah yang sangat mudah digunakan:

```
+-----------------------------------------------------------------------------+
|  BootBridge Remote Desktop                                                 |
+-----------------------------------------------------------------------------+
|  [ID Komputer Anda / My ID]  192.168.1.15         [ Salin ID / Copy ]       |
+-----------------------------------------------------------------------------+
|  ID Komputer Partner:       [ 192.168.1.100                    ]          |
|  Komputer Terdeteksi Wi-Fi: [ LAPTOP-WINDOWS (192.168.1.100) v ] [ Pindai ] |
+-----------------------------------------------------------------------------+
|  [ SAMBUNGKAN SEKARANG (1-KLIK) ]                                           |
+-----------------------------------------------------------------------------+
```

### Alur Kerja Remote Desktop 7-Langkah:

1. **Langkah 1 & 2 (Pemasangan Otomatis Komponen)**: BootBridge memeriksa ketersediaan client remote saat aplikasi dibuka. Komponen yang belum ada bisa dipasang otomatis dengan 1 klik.
2. **Langkah 3 (ID Perangkat Anda)**: ID / Alamat IP unik kamu ditampilkan di banner atas lengkap dengan tombol **Salin ID** 1-klik untuk dibagikan.
3. **Langkah 4 (Koneksi ke Perangkat Remote - Attended Access)**: Masukkan ID / IP komputer tujuan (atau klik **Pindai Wi-Fi** untuk menemukan PC Windows di sekitar) lalu klik **SAMBUNGKAN SEKARANG**.
4. **Langkah 5 (Pengaturan Unattended Access)**: Simpan kredensial login Windows target untuk terhubung kapan saja tanpa butuh persetujuan manual di sisi target.
5. **Langkah 6 (Kontrol Penuh)**: Dapatkan kontrol mouse, keyboard, clipboard copy-paste dua arah, passthrough audio, dan penyesuaian resolusi layar secara dinamis.
6. **Langkah 7 (Keamanan Terenkripsi)**: Seluruh koneksi remote desktop dienkripsi dan terlindungi.

---

## Matriks Perbandingan

| Fitur | Dual-Boot Restart Fisik | Virtual Machine Standar | BootBridge |
| :--- | :---: | :---: | :---: |
| **Perlu Reboot / Restart** | Ya | Tidak | **Tidak** |
| **Menggunakan Windows Fisik Terinstall**| Ya | Tidak (Perlu install OS ulang) | **Ya** |
| **Performa** | 100% Native | 60% - 80% Virtualized | **90% - 98% Mendekati Native** |
| **Format Installer Native** | N/A | Terbatas | **.exe (Win), .dmg (Mac), .deb (Linux)** |
| **Dukungan Lintas Platform** | N/A | Ya | **Ya (Linux, macOS, Windows)** |
| **Perlindungan Keamanan Disk** | Tidak Ada | N/A | **Automated Mount Protection Guard** |
| **Fitur Remote Desktop** | Tidak Ada | Terbatas | **Modul Remote 7-Langkah Praktis** |
| **Penggunaan Memory (RAM)** | N/A | 500 MB+ (Web wrapper) | **~30 – 50 MB (Native GTK/Tkinter)** |

---

## Arsitektur Sistem

```mermaid
flowchart TD
    subgraph Host ["Sistem Operasi Utama (Linux / macOS / Windows)"]
        UI["Aplikasi BootBridge"]
        SC["Protokol Safety Checker"]
        DM["Manajer Disk"]
        TPM["swtpm (Daemon TPM 2.0)"]
        QEMU["Mesin Hypervisor QEMU"]
    end

    subgraph Hardware ["Penyimpanan Hardware Fisik"]
        DISK[("Drive Disk Fisik")]
        ESP["Partisi Sistem EFI"]
        WIN["Volume Windows OS (NTFS)"]
    end

    subgraph Guest ["Virtual Machine Windows Guest"]
        OVMF["Firmware UEFI OVMF"]
        WINOS["Kernel Windows 10/11 Fisik"]
    end

    UI -->|1. Deteksi Disk & OS| DM
    DM -->|2. Cek Status Mount| DISK
    UI -->|3. Evaluasi Aturan Safety| SC
    SC -->|4. Unmount NTFS Aman| DM
    UI -->|5. Jalankan Daemon TPM| TPM
    UI -->|6. Eksekusi Passthrough| QEMU
    QEMU -->|7. Akses Drive Fisik| DISK
    DISK --> ESP & WIN
    QEMU -->|8. Oper Kontrol via OVMF| OVMF
    OVMF -->|9. Boot Kernel| WINOS

    style SC fill:#1f6feb,stroke:#fff,stroke-width:2px,color:#fff
    style QEMU fill:#ff6600,stroke:#fff,stroke-width:2px,color:#fff
    style WINOS fill:#00599c,stroke:#fff,stroke-width:2px,color:#fff
```

---

## Persyaratan Sistem

| Komponen | Spesifikasi Minimum | Spesifikasi Direkomendasikan |
| :--- | :--- | :--- |
| **Sistem Operasi Host** | Linux, macOS (10.15+), atau Windows 10/11 | Linux Mint, Ubuntu 22.04+, macOS 12+, Windows 11 |
| **Virtualisasi CPU** | Intel VT-x atau AMD-V aktif di BIOS/UEFI | CPU 4+ Cores dengan Hardware Virtualization |
| **Memori Utama (RAM)** | 8 GB Total RAM Sistem | 16 GB+ Total RAM Sistem |
| **Antarmuka Penyimpanan** | Setup Dual-Boot SATA SSD / HDD | Setup Dual-Boot NVMe M.2 SSD |

---

## Panduan Penggunaan

1. **Jalankan BootBridge**:
   Buka melalui shortcut aplikasi atau jalankan `bootbridge` di terminal.

2. **Pilih Disk Fisik Target**:
   Pilih drive fisik yang berisi instalasi Windows kamu di menu dropdown **Target Disk**.

3. **Verifikasi Status Safety Guard**:
   - Jika partisi NTFS sedang di-mount oleh sistem operasi host, klik **`Unmount Partisi Secara Aman`**.
   - Jika Windows terkunci oleh Fast Startup, klik **`Reset Status NTFS / Fast Startup`**.

4. **Jalankan VM**:
   Klik **`MULAI VM WINDOWS`**. Jendela VM akan langsung memuat desktop Windows fisik kamu.

---

## Troubleshooting & FAQ

### 1. Mematikan / Mengaktifkan Windows Fast Startup

> [!IMPORTANT]
> Ketika Windows dimatikan secara fisik dengan fitur **Fast Startup** aktif, Windows akan menghibernasi kernel dan mengunci filesystem NTFS. Memboot QEMU saat status terhibernasi akan memaksa Windows masuk ke dalam loop *Automatic Repair*.

**Solusi:**
- Gunakan tombol internal **`Reset Status NTFS / Fast Startup`** di BootBridge untuk membersihkan kunci hibernasi.
- Atau boot ke Windows fisik dan jalankan perintah `powercfg /h off` di Command Prompt (CMD) sebagai Administrator.

---

## Pintasan Keyboard (Shortcuts)

| Pintasan | Fungsi | Keterangan |
| :--- | :--- | :--- |
| **`Ctrl + Alt + F`** | **Toggle Fullscreen VM** | Berpindah antara mode jendela dan mode layar penuh VM |
| **`Ctrl + Alt + G`** | **Lepas / Tangkap Fokus** | Melepas atau menangkap fokus kursor mouse dan keyboard |
| **`F11`** | **Fullscreen Jendela Utama** | Mengubah mode layar penuh jendela aplikasi BootBridge |
| **`Ctrl + C` / `Ctrl + V`** | **Shared Clipboard** | Copy dan paste teks dua arah antara Host dan VM |
| **`Super / Tombol Windows`** | **Menu Start Windows** | Ditangkap langsung oleh Start Menu Windows VM saat jendela aktif |

---

## Kontribusi & Lisensi

Kontribusi sangat disambut! Silakan baca [CONTRIBUTING.md](CONTRIBUTING.md) untuk detail pengiriman Pull Request.

### Lisensi

Proyek ini dilesensikan di bawah **Lisensi MIT** - lihat file [LICENSE](LICENSE) untuk detailnya.

---

<div align="center">

Dikembangkan oleh **[Rizky Ibrahim Nasrullah (dreamzz2nd)](https://github.com/dreamzz2nd)**

*BootBridge adalah aplikasi independen open-source.*

</div>
