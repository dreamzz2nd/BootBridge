import os
import subprocess
import shutil
import json

class SafetyChecker:
    """Performs pre-flight safety validation before launching Windows VM."""

    OVMF_SEARCH_PATHS = [
        "/usr/share/OVMF/OVMF_CODE_4M.fd",
        "/usr/share/OVMF/OVMF_CODE_4M.secboot.fd",
        "/usr/share/OVMF/OVMF_CODE.fd",
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
        "/usr/share/edk2/x64/OVMF_VARS.fd",
        "/usr/share/edk2-ovmf/x64/OVMF_VARS.fd",
        "/usr/share/edk2/ovmf/OVMF_VARS.fd",
        "/usr/share/qemu/OVMF_VARS.fd",
        "/usr/share/qemu/ovmf-x86_64-vars.bin"
    ]

    @classmethod
    def check_system_dependencies(cls):
        """Checks for required system packages: QEMU, OVMF firmware, KVM, pkexec."""
        status = {
            "qemu_installed": False,
            "qemu_path": None,
            "ovmf_installed": False,
            "ovmf_code": None,
            "ovmf_vars": None,
            "kvm_available": os.path.exists("/dev/kvm"),
            "pkexec_installed": bool(shutil.which("pkexec")),
            "udisksctl_installed": bool(shutil.which("udisksctl")),
            "missing_packages": [],
            "install_command": "sudo apt install -y qemu-system-x86-64 ovmf qemu-utils"
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

if __name__ == "__main__":
    deps = SafetyChecker.check_system_dependencies()
    print("System Dependencies Check:")
    print(json.dumps(deps, indent=2))
