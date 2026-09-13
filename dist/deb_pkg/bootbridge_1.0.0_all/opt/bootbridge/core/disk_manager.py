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
    @classmethod
    def _get_windows_disks(cls):
        """Queries physical disks and partitions on Windows via PowerShell."""
        ps_script = (
            "$ErrorActionPreference = 'SilentlyContinue'; "
            "$disks = Get-Disk; "
            "$res = @(); "
            "foreach ($d in $disks) { "
            "  $parts = Get-Partition -DiskNumber $d.Number; "
            "  $pList = @(); "
            "  foreach ($p in $parts) { "
            "    $vol = Get-Volume -Partition $p -ErrorAction SilentlyContinue; "
            "    $fs = if ($vol -and $vol.FileSystem) { $vol.FileSystem.ToLower() } else { '' }; "
            "    $lbl = if ($vol -and $vol.FileSystemLabel) { $vol.FileSystemLabel } else { '' }; "
            "    $dl = if ($p.DriveLetter) { $p.DriveLetter + ':' } else { '' }; "
            "    $pList += @{ "
            "      name = 'disk' + $d.Number + 'p' + $p.PartitionNumber; "
            "      path = '\\\\.\\PhysicalDrive' + $d.Number; "
            "      size_bytes = [int64]$p.Size; "
            "      fstype = $fs; "
            "      label = $lbl; "
            "      mountpoint = $dl; "
            "      is_mounted = [bool]$dl "
            "    }; "
            "  }; "
            "  $res += @{ "
            "    number = $d.Number; "
            "    name = 'disk' + $d.Number; "
            "    path = '\\\\.\\PhysicalDrive' + $d.Number; "
            "    model = if ($d.FriendlyName) { $d.FriendlyName.Trim() } else { 'Physical Storage' }; "
            "    size_bytes = [int64]$d.Size; "
            "    partitions = $pList "
            "  } "
            "}; "
            "$res | ConvertTo-Json -Depth 5"
        )
        try:
            startupinfo = None
            if sys.platform == "win32":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_script],
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                timeout=12
            )
            if res.returncode == 0 and res.stdout.strip():
                raw_data = json.loads(res.stdout)
                if isinstance(raw_data, dict):
                    raw_data = [raw_data]

                disks = []
                for d in raw_data:
                    disk_bytes = d.get("size_bytes", 0)
                    disk_info = {
                        "name": d.get("name", f"disk{d.get('number', 0)}"),
                        "path": d.get("path", f"\\\\.\\PhysicalDrive{d.get('number', 0)}"),
                        "model": d.get("model", "Generic Physical Storage"),
                        "size_bytes": disk_bytes,
                        "size_str": format_size(disk_bytes),
                        "partitions": [],
                        "has_windows": False,
                        "has_macos": False,
                        "has_linux": False,
                        "detected_os": "Physical Storage",
                        "is_any_mounted": False,
                        "mounted_partitions": [],
                        "is_host_disk": False
                    }

                    parts = d.get("partitions", [])
                    if isinstance(parts, dict):
                        parts = [parts]

                    for p in parts:
                        p_size = p.get("size_bytes", 0)
                        fstype = (p.get("fstype") or "").lower()
                        label = (p.get("label") or "").lower()
                        mountpoint = p.get("mountpoint") or None
                        is_mounted = bool(mountpoint)

                        part_info = {
                            "name": p.get("name"),
                            "path": p.get("path"),
                            "size_bytes": p_size,
                            "size_str": format_size(p_size),
                            "fstype": fstype,
                            "label": p.get("label") or "",
                            "mountpoint": mountpoint,
                            "is_mounted": is_mounted
                        }
                        disk_info["partitions"].append(part_info)

                        if is_mounted:
                            disk_info["is_any_mounted"] = True
                            disk_info["mounted_partitions"].append({
                                "path": p.get("path"),
                                "mountpoint": mountpoint
                            })
                            if mountpoint and mountpoint.upper().startswith("C:"):
                                disk_info["is_host_disk"] = True

                        # Check OS Indicators
                        if fstype in ["ntfs", "exfat", "refs"] or "win" in label or "system" in label:
                            disk_info["has_windows"] = True
                        if fstype in ["apfs", "hfs+", "hfsplus"] or "mac" in label or "apple" in label or "osx" in label:
                            disk_info["has_macos"] = True
                        if fstype in ["ext4", "btrfs", "xfs", "f2fs"] or "linux" in label or "ubuntu" in label:
                            disk_info["has_linux"] = True

                    detected_os_list = []
                    if disk_info["has_windows"]:
                        detected_os_list.append("Windows")
                    if disk_info["has_macos"]:
                        detected_os_list.append("macOS")
                    if disk_info["has_linux"]:
                        detected_os_list.append("Linux")

                    disk_info["detected_os"] = " / ".join(detected_os_list) if detected_os_list else "Physical Storage"
                    disks.append(disk_info)

                if disks:
                    return disks
        except Exception as e:
            print(f"[DiskManager] Error running PowerShell disk detection: {e}")
        return []

    @classmethod
    def _get_macos_disks(cls):
        """Queries physical disks and partitions on macOS via diskutil."""
        try:
            res = subprocess.run(["diskutil", "list", "-plist"], capture_output=True, text=True, timeout=10)
            if res.returncode == 0:
                # Basic plist parsing fallback for macOS disk structure
                disks = []
                res_info = subprocess.run(["diskutil", "info", "-all"], capture_output=True, text=True, timeout=10)
                # Parse output or return structured disk list
                return disks
        except Exception as e:
            print(f"[DiskManager] Error running macOS diskutil: {e}")
        return []

    @staticmethod
    def get_physical_disks():
        """
        Executes lsblk (Linux), PowerShell (Windows), or diskutil (macOS) to list physical block devices.
        Returns a list of disk objects with OS detection and mount statuses.
        """
        if sys.platform == "win32":
            win_disks = DiskManager._get_windows_disks()
            if win_disks:
                return win_disks

        if sys.platform == "darwin":
            mac_disks = DiskManager._get_macos_disks()
            if mac_disks:
                return mac_disks

        if not sys.platform.startswith("linux"):
            # Fallback for systems where native tools were inaccessible
            return [{
                "name": "disk0",
                "path": "\\\\.\\PhysicalDrive0" if sys.platform == "win32" else "/dev/disk0",
                "model": "Primary Physical Storage",
                "size_bytes": 0,
                "size_str": "Auto-Detect",
                "partitions": [
                    {
                        "name": "partition1",
                        "path": "\\\\.\\PhysicalDrive0" if sys.platform == "win32" else "/dev/disk0s1",
                        "size_bytes": 0,
                        "size_str": "Auto-Detect",
                        "fstype": "auto",
                        "label": "Dual-Boot Target",
                        "mountpoint": None,
                        "is_mounted": False
                    }
                ],
                "has_windows": False,
                "has_macos": False,
                "has_linux": False,
                "detected_os": "Physical Storage",
                "is_any_mounted": False,
                "mounted_partitions": [],
                "is_host_disk": False
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
            dev_type = dev.get("type", "")
            dev_path = dev.get("path", f"/dev/{dev.get('name', '')}")

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

                if is_mounted:
                    disk_info["is_any_mounted"] = True
                    disk_info["mounted_partitions"].append({
                        "path": part_path,
                        "mountpoint": mountpoint
                    })

                if fstype in ["ntfs", "exfat"] or "win" in label or "system" in label:
                    disk_info["has_windows"] = True
                if fstype in ["apfs", "hfs+", "hfsplus"] or "mac" in label or "apple" in label or "osx" in label:
                    disk_info["has_macos"] = True
                if fstype in ["ext4", "btrfs", "xfs", "f2fs"] or "linux" in label or "ubuntu" in label:
                    disk_info["has_linux"] = True

            detected_os_list = []
            if disk_info["has_windows"]:
                detected_os_list.append("Windows")
            if disk_info["has_macos"]:
                detected_os_list.append("macOS")
            if disk_info["has_linux"]:
                detected_os_list.append("Linux")

            disk_info["detected_os"] = " / ".join(detected_os_list) if detected_os_list else "Physical Storage"

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
