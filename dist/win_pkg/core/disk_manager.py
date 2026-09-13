import subprocess
import json
import os
import re
import sys

def format_size(size_bytes):
    """Formats bytes into human readable string (GB, MB)."""
    try:
        size_bytes = int(size_bytes)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} PB"
    except Exception:
        return "Unknown"

class DiskManager:
    """Manages physical disk and partition detection for dual-boot OS installations."""

    @staticmethod
    def get_physical_disks():
        """
        Executes lsblk (Linux) or platform-specific tools to list physical block devices.
        Returns a list of disk objects with Windows detection and mount statuses.
        """
        if not sys.platform.startswith("linux"):
            # Fallback for Windows/macOS testing or non-Linux execution
            return [{
                "name": "disk0",
                "path": "\\\\.\\PhysicalDrive0" if sys.platform == "win32" else "/dev/disk0",
                "model": "Host Primary Storage",
                "size_bytes": 512 * 1024 * 1024 * 1024,
                "size_str": "512.0 GB",
                "partitions": [
                    {
                        "name": "disk0s2",
                        "path": "\\\\.\\PhysicalDrive0" if sys.platform == "win32" else "/dev/disk0s2",
                        "size_bytes": 500 * 1024 * 1024 * 1024,
                        "size_str": "500.0 GB",
                        "fstype": "ntfs",
                        "label": "Windows System",
                        "mountpoint": None,
                        "is_mounted": False
                    }
                ],
                "has_windows": True,
                "is_any_mounted": False,
                "mounted_partitions": []
            }]

        cmd = [
            "lsblk", "-J", "-b",
            "-o", "NAME,PATH,SIZE,TYPE,FSTYPE,LABEL,MOUNTPOINT,UUID,MODEL"
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(res.stdout)
        except Exception as e:
            print(f"[DiskManager] Error running lsblk: {e}")
            return []

        devices = data.get("blockdevices", [])
        disks = []

        for dev in devices:
            # We focus on physical disks or loop devices with partitions
            dev_type = dev.get("type", "")
            dev_path = dev.get("path", f"/dev/{dev.get('name', '')}")
            
            # Skip read-only CD-ROMs / RAM disks if not useful
            if dev_type not in ["disk", "mpath", "mmc"]:
                if not dev.get("children"):
                    continue

            disk_info = {
                "name": dev.get("name"),
                "path": dev_path,
                "model": (dev.get("model") or "Generic Storage").strip(),
                "size_bytes": dev.get("size", 0),
                "size_str": format_size(dev.get("size", 0)),
                "partitions": [],
                "has_windows": False,
                "has_macos": False,
                "has_linux": False,
                "detected_os": "Unknown",
                "is_any_mounted": False,
                "mounted_partitions": []
            }

            children = dev.get("children", [])
            for child in children:
                mountpoint = child.get("mountpoint")
                fstype = (child.get("fstype") or "").lower()
                label = (child.get("label") or "").lower()
                part_path = child.get("path", f"/dev/{child.get('name', '')}")

                is_mounted = bool(mountpoint)
                
                part_info = {
                    "name": child.get("name"),
                    "path": part_path,
                    "size_bytes": child.get("size", 0),
                    "size_str": format_size(child.get("size", 0)),
                    "fstype": fstype,
                    "label": child.get("label") or "",
                    "mountpoint": mountpoint,
                    "is_mounted": is_mounted
                }
                disk_info["partitions"].append(part_info)

                # Check if partition is mounted by host OS
                if is_mounted:
                    disk_info["is_any_mounted"] = True
                    disk_info["mounted_partitions"].append({
                        "path": part_path,
                        "mountpoint": mountpoint
                    })

                # Check OS Indicators
                if fstype in ["ntfs", "exfat"] or "win" in label or "system" in label:
                    disk_info["has_windows"] = True
                if fstype in ["apfs", "hfs+", "hfsplus"] or "mac" in label or "apple" in label or "osx" in label:
                    disk_info["has_macos"] = True
                if fstype in ["ext4", "btrfs", "xfs", "f2fs"] or "linux" in label or "ubuntu" in label:
                    disk_info["has_linux"] = True

            # Determine Primary Detected Guest OS
            detected_os_list = []
            if disk_info["has_windows"]:
                detected_os_list.append("Windows")
            if disk_info["has_macos"]:
                detected_os_list.append("macOS")
            if disk_info["has_linux"]:
                detected_os_list.append("Linux")

            disk_info["detected_os"] = " / ".join(detected_os_list) if detected_os_list else "Physical Storage"

            # Check if root/system partition is on this disk
            disk_info["is_host_disk"] = any(
                p["mountpoint"] in ["/", "/boot", "/boot/efi"] for p in disk_info["partitions"]
            )

            disks.append(disk_info)

        return disks

if __name__ == "__main__":
    disks = DiskManager.get_physical_disks()
    print(f"Found {len(disks)} physical disks:")
    for d in disks:
        print(f"- {d['path']} ({d['model']}, {d['size_str']}): WindowsDetected={d['has_windows']}, AnyMounted={d['is_any_mounted']}")
        for p in d['partitions']:
            print(f"    * {p['path']} [{p['fstype']}] size={p['size_str']} label='{p['label']}' mounted={p['mountpoint']}")
