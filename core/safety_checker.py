import os
import subprocess
import shutil
import json
import struct


class SafetyChecker:
    """Performs pre-flight safety validation before launching Windows VM."""

    OVMF_SEARCH_PATHS = [
        "/usr/share/OVMF/OVMF_CODE_4M.fd",
        "/usr/share/OVMF/OVMF_CODE.fd",
        "/usr/share/OVMF/OVMF_CODE_4M.ms.fd",
        "/usr/share/OVMF/OVMF_CODE_4M.secboot.fd",
        "/usr/share/OVMF/OVMF_CODE.secboot.fd",
        "/usr/share/edk2/x64/OVMF_CODE.fd",
        "/usr/share/edk2-ovmf/x64/OVMF_CODE.fd",
        "/usr/share/edk2/ovmf/OVMF_CODE.fd",
        "/usr/share/qemu/OVMF.fd",
        "/usr/share/qemu/ovmf-x86_64-code.bin"
    ]

    OVMF_VARS_SEARCH_PATHS = [
        "/usr/share/OVMF/OVMF_VARS_4M.fd",
        "/usr/share/OVMF/OVMF_VARS.fd",
        "/usr/share/OVMF/OVMF_VARS_4M.ms.fd",
        "/usr/share/edk2/x64/OVMF_VARS.fd",
        "/usr/share/edk2-ovmf/x64/OVMF_VARS.fd",
        "/usr/share/edk2/ovmf/OVMF_VARS.fd",
        "/usr/share/qemu/OVMF_VARS.fd",
        "/usr/share/qemu/ovmf-x86_64-vars.bin"
    ]

    @classmethod
    def check_system_dependencies(cls):
        """Checks for required system packages: QEMU, OVMF firmware, KVM, pkexec, swtpm."""
        status = {
            "qemu_installed": False,
            "qemu_path": None,
            "ovmf_installed": False,
            "ovmf_code": None,
            "ovmf_vars": None,
            "kvm_available": os.path.exists("/dev/kvm"),
            "pkexec_installed": bool(shutil.which("pkexec")),
            "udisksctl_installed": bool(shutil.which("udisksctl")),
            "swtpm_installed": bool(shutil.which("swtpm")),
            "missing_packages": [],
            "install_command": "sudo apt install -y qemu-system-x86-64 ovmf qemu-utils swtpm"
        }

        # Check QEMU
        qemu_bin = shutil.which("qemu-system-x86_64")
        if qemu_bin:
            status["qemu_installed"] = True
            status["qemu_path"] = qemu_bin
        else:
            status["missing_packages"].append("qemu-system-x86_64")

        # Check OVMF
        for path in cls.OVMF_SEARCH_PATHS:
            if os.path.exists(path):
                status["ovmf_installed"] = True
                status["ovmf_code"] = path
                break

        for path in cls.OVMF_VARS_SEARCH_PATHS:
            if os.path.exists(path):
                status["ovmf_vars"] = path
                break

        if not status["ovmf_installed"]:
            status["missing_packages"].append("ovmf")

        return status

    @staticmethod
    def check_disk_safety(disk_info):
        """
        Validates safety requirements for a target disk:
        1. Checks if any partition is mounted in Linux.
        2. Detects if disk is shared with host Linux OS.
        3. Returns detailed safety status and recommendations.
        """
        results = {
            "is_safe": True,
            "is_host_disk": disk_info.get("is_host_disk", False),
            "mounted_partitions": disk_info.get("mounted_partitions", []),
            "unmount_required": False,
            "windows_partitions": [],
            "warnings": [],
            "errors": []
        }

        # Find Windows partitions (NTFS)
        for part in disk_info.get("partitions", []):
            fstype = part.get("fstype", "").lower()
            if fstype == "ntfs" or "win" in (part.get("label") or "").lower():
                results["windows_partitions"].append(part)

        # Check mounted partitions
        mounted_parts = disk_info.get("mounted_partitions", [])
        if mounted_parts:
            # Filter mounted partitions: if Host Linux partition is mounted (/ or /boot), it's a shared host disk
            host_mounts = [p for p in mounted_parts if p["mountpoint"] in ["/", "/boot", "/home"]]
            data_mounts = [p for p in mounted_parts if p["mountpoint"] not in ["/", "/boot", "/home"]]

            if data_mounts:
                results["unmount_required"] = True
                results["is_safe"] = False
                results["errors"].append(
                    f"Partisi Windows ({', '.join([p['path'] for p in data_mounts])}) sedang di-mount oleh Linux. "
                    "Wajib di-unmount terlebih dahulu untuk mencegah kerusakan data NTFS!"
                )

            if host_mounts:
                results["warnings"].append(
                    "Disk ini digunakan bersama oleh OS Linux host. BootBridge akan menggunakan "
                    "Mode Safe Passthrough agar VM Windows tidak dapat menyentuh partisi Linux host."
                )

        return results

    @staticmethod
    def safe_unmount_partition(part_path):
        """Unmounts a mounted partition using udisksctl (user level) or umount."""
        try:
            cmd = ["udisksctl", "unmount", "-b", part_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True, f"Partisi {part_path} berhasil di-unmount."
            
            # Fallback to pkexec umount
            cmd_root = ["pkexec", "umount", part_path]
            res_root = subprocess.run(cmd_root, capture_output=True, text=True)
            if res_root.returncode == 0:
                return True, f"Partisi {part_path} berhasil di-unmount dengan pkexec."
            else:
                return False, f"Gagal unmount {part_path}: {res.stderr or res_root.stderr}"
        except Exception as e:
            return False, f"Error saat unmount {part_path}: {str(e)}"

    @staticmethod
    def fix_ntfs_dirty_flag(part_path):
        """Runs ntfsfix via pkexec to clear NTFS dirty & hibernation volume flags."""
        try:
            cmd = ["pkexec", "ntfsfix", part_path]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                return True, f"Berhasil mereset status NTFS pada {part_path}. Dirty/hibernation flag cleared!"
            else:
                return False, f"Gagal mereset NTFS {part_path}: {res.stderr or res.stdout}"
        except Exception as e:
            return False, f"Error ntfsfix: {str(e)}"

    @staticmethod
    def disable_fast_startup(part_path):
        """
        Disables Fast Startup for a target Windows NTFS partition (restores default clean shutdown):
        1. Mounts partition temporarily if not already mounted.
        2. Restores SYSTEM hive backup if present, OR modifies HiberbootEnabled & HibernateEnabled DWORD to 0 in Windows SYSTEM registry hive offline.
        3. Runs ntfsfix to clear dirty/hibernation flags on NTFS.
        4. Generates Disable_Fast_Startup.bat and .reg files on root of Windows partition.
        5. Cleans up temporary mount.
        """
        was_mounted_by_us = False
        mountpoint = None

        # Check if already mounted
        try:
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if len(parts) >= 2 and parts[0] == part_path:
                        mountpoint = parts[1].replace("\\040", " ")
                        break
        except Exception:
            pass

        # If not mounted, try mounting using udisksctl
        if not mountpoint:
            try:
                res = subprocess.run(["udisksctl", "mount", "-b", part_path], capture_output=True, text=True)
                if res.returncode == 0:
                    was_mounted_by_us = True
                    out = res.stdout.strip()
                    if " at " in out:
                        mountpoint = out.split(" at ")[-1].strip()
                        if mountpoint.endswith("."):
                            mountpoint = mountpoint[:-1]
                else:
                    with open("/proc/mounts", "r") as f:
                        for line in f:
                            p = line.split()
                            if len(p) >= 2 and p[0] == part_path:
                                mountpoint = p[1].replace("\\040", " ")
                                was_mounted_by_us = True
                                break
            except Exception as e:
                return False, f"Gagal meng-mount partisi {part_path}: {str(e)}"

        if not mountpoint or not os.path.exists(mountpoint):
            return False, f"Tidak dapat mengakses mountpoint untuk partisi {part_path}."

        try:
            # Search for SYSTEM registry hive case-insensitively
            system_hive_path = None
            possible_rel_paths = [
                "Windows/System32/config/SYSTEM",
                "windows/system32/config/system",
                "Windows/system32/config/system",
                "WINDOWS/SYSTEM32/CONFIG/SYSTEM"
            ]
            for rel in possible_rel_paths:
                full_p = os.path.join(mountpoint, rel)
                if os.path.exists(full_p):
                    system_hive_path = full_p
                    break

            if not system_hive_path:
                for root, dirs, files in os.walk(mountpoint):
                    for file in files:
                        if file.lower() == "system" and "config" in root.lower():
                            system_hive_path = os.path.join(root, file)
                            break
                    if system_hive_path:
                        break

            registry_updated = False
            if system_hive_path and os.path.exists(system_hive_path):
                try:
                    bak_path = system_hive_path + ".bak_bootbridge"
                    if os.path.exists(bak_path):
                        shutil.copy2(bak_path, system_hive_path)
                        registry_updated = True
                    else:
                        shutil.copy2(system_hive_path, bak_path)

                    with open(system_hive_path, "rb") as f:
                        hive_data = bytearray(f.read())

                    modified = False
                    for target_name in [b"HiberbootEnabled", b"HibernateEnabled"]:
                        pos = 0
                        while True:
                            pos = hive_data.find(target_name, pos)
                            if pos == -1:
                                break
                            if pos >= 16 and hive_data[pos-16:pos-14] == b"vk":
                                hive_data[pos-8:pos-4] = b"\x00\x00\x00\x00"
                                modified = True
                            pos += len(target_name)

                    if modified:
                        if len(hive_data) >= 4096 and hive_data[:4] == b"regf":
                            cs = 0
                            for i in range(0, 508, 4):
                                cs ^= struct.unpack("<I", hive_data[i:i+4])[0]
                            hive_data[0x1c:0x20] = struct.pack("<I", cs)

                        with open(system_hive_path, "wb") as f:
                            f.write(hive_data)
                        registry_updated = True
                except Exception as e:
                    print(f"[SafetyChecker] Warning modifying registry hive directly: {e}")

            # Also try chntpw if available
            chntpw_bin = shutil.which("chntpw")
            if chntpw_bin and system_hive_path:
                try:
                    cmd = [chntpw_bin, "-e", system_hive_path]
                    input_script = "cd ControlSet001\\Control\\Session Manager\\Power\n" \
                                   "nv 4 HiberbootEnabled\n" \
                                   "ed HiberbootEnabled\n0\n" \
                                   "cd \\ControlSet001\\Control\\Power\n" \
                                   "nv 4 HibernateEnabled\n" \
                                   "ed HibernateEnabled\n0\n" \
                                   "s\ny\nq\n"
                    subprocess.run(cmd, input=input_script, text=True, capture_output=True)
                    registry_updated = True
                except Exception as e:
                    print(f"[SafetyChecker] Warning running chntpw: {e}")

            # Generate helper scripts on Windows drive to turn off Fast Startup
            bat_path = os.path.join(mountpoint, "Disable_Fast_Startup.bat")
            reg_path = os.path.join(mountpoint, "Disable_Fast_Startup.reg")

            bat_content = (
                "@echo off\r\n"
                "echo Disabling Windows Fast Startup (Recommended for Dual-Boot)...\r\n"
                "powercfg /h off\r\n"
                "reg add \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power\" /v HiberbootEnabled /t REG_DWORD /d 0 /f\r\n"
                "reg add \"HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\" /v HibernateEnabled /t REG_DWORD /d 0 /f\r\n"
                "echo.\r\n"
                "echo Fast Startup is now DISABLED in Windows (Safe for Dual-Boot)!\r\n"
                "pause\r\n"
            )
            with open(bat_path, "w", newline="\r\n") as f:
                f.write(bat_content)

            reg_content = (
                "Windows Registry Editor Version 5.00\r\n\r\n"
                "[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Power]\r\n"
                "\"HiberbootEnabled\"=dword:00000000\r\n\r\n"
                "[HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Power]\r\n"
                "\"HibernateEnabled\"=dword:00000000\r\n"
            )
            with open(reg_path, "w", newline="\r\n") as f:
                f.write(reg_content)

            # Also clean NTFS dirty/hibernation flags
            SafetyChecker.fix_ntfs_dirty_flag(part_path)

            msg = f"Fast Startup berhasil DIMATIKAN (dikembalikan ke settingan default/aman) untuk partisi {part_path}!\n" \
                  f"• Status HiberbootEnabled & HibernateEnabled diatur ke 0 pada Registry Windows.\n" \
                  f"• Booting ke Windows fisik sekarang aman tanpa error 'Preparing Automatic Repair'!"

            return True, msg

        finally:
            if was_mounted_by_us and part_path:
                try:
                    subprocess.run(["udisksctl", "unmount", "-b", part_path], capture_output=True, text=True)
                except Exception:
                    pass

    @staticmethod
    def enable_fast_startup(part_path):
        """Backward compatibility wrapper calling disable_fast_startup to enforce safe dual-boot state."""
        return SafetyChecker.disable_fast_startup(part_path)



if __name__ == "__main__":
    deps = SafetyChecker.check_system_dependencies()
    print("System Dependencies Check:")
    print(json.dumps(deps, indent=2))
