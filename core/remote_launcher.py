"""
Remote Desktop Connection Launcher for BootBridge
Supports RDP (FreeRDP), SPICE, and VNC protocols
"""

import os
import shutil
import subprocess
import threading
import time
import socket
import ipaddress

import sys

class RemoteLauncher:
    """Manages remote desktop connection processes (RDP, SPICE, VNC) and network discovery."""

    def __init__(self, log_callback=None, status_callback=None):
        self.process = None
        self.is_running = False
        self.log_callback = log_callback or (lambda text: print(f"[Remote] {text}"))
        self.status_callback = status_callback or (lambda status: None)
        self.monitor_thread = None

    @classmethod
    def check_remote_dependencies(cls):
        """Checks for installed remote client binaries: xfreerdp, mstsc (Windows native), spicy, remote-viewer, vncviewer."""
        is_win = sys.platform == "win32"
        mstsc_path = shutil.which("mstsc") or (r"C:\Windows\System32\mstsc.exe" if is_win and os.path.exists(r"C:\Windows\System32\mstsc.exe") else None)

        clients = {
            "freerdp": mstsc_path if is_win else (shutil.which("xfreerdp") or shutil.which("freerdp")),
            "spicy": shutil.which("spicy") or shutil.which("remote-viewer"),
            "vnc": shutil.which("vncviewer") or shutil.which("xvnc4viewer")
        }

        install_cmds = {
            "debian": "sudo apt install -y freerdp2-x11 spice-client-gtk tigervnc-viewer",
            "arch": "sudo pacman -S freerdp spice-gtk tigervnc",
            "fedora": "sudo dnf install -y freerdp spice-gtk-tools tigervnc",
            "mac": "brew install freerdp virt-viewer"
        }

        return {
            "clients": clients,
            "has_rdp": bool(clients["freerdp"]),
            "has_spice": bool(clients["spicy"]),
            "has_vnc": bool(clients["vnc"]),
            "install_cmd": install_cmds["debian"] if sys.platform.startswith("linux") else install_cmds.get("mac", "")
        }

    @classmethod
    def install_remote_dependencies(cls, log_callback=None):
        """1-Click automated installer for missing remote desktop client packages using pkexec."""
        cb = log_callback or (lambda msg: print(msg))
        cb("Memulai instalasi otomatis komponen Remote Desktop (freerdp2-x11, spice-client-gtk)...")

        pkexec_bin = shutil.which("pkexec")
        if not pkexec_bin:
            cb("Error: pkexec tidak ditemukan. Harap install paket secara manual dari Terminal.")
            return False, "pkexec tidak ditemukan"

        cmd = ["pkexec", "apt", "install", "-y", "freerdp2-x11", "spice-client-gtk", "tigervnc-viewer"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode == 0:
                cb("Berhasil menginstal komponen Remote Desktop!")
                return True, "Instalasi Berhasil"
            else:
                err_msg = res.stderr or res.stdout
                cb(f"Gagal menginstal paket: {err_msg}")
                return False, f"Gagal: {err_msg}"
        except Exception as e:
            cb(f"Error instalasi: {str(e)}")
            return False, str(e)

    @classmethod
    def scan_local_network(cls, callback=None):
        """Asynchronously scans local Wi-Fi/LAN subnet for Windows PCs with open RDP (3389) or SPICE (5900) ports."""
        def run_scan():
            local_ip = "127.0.0.1"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(('8.8.8.8', 80))
                local_ip = s.getsockname()[0]
                s.close()
            except Exception:
                pass

            if local_ip == "127.0.0.1":
                if callback:
                    callback([])
                return

            detected = []
            threads = []
            try:
                net = ipaddress.ip_network(f"{local_ip}/24", strict=False)
                hosts = list(net.hosts())[:150]
            except Exception:
                hosts = []

            def check_host(ip_str, port):
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(0.3)
                    if sock.connect_ex((ip_str, port)) == 0:
                        proto = "rdp" if port == 3389 else "spice"
                        label = f"Windows PC ({ip_str}) [{proto.upper()}]"
                        detected.append({"host": ip_str, "port": port, "proto": proto, "label": label})
                    sock.close()
                except Exception:
                    pass

            for host in hosts:
                for port in [3389, 5900]:
                    t = threading.Thread(target=check_host, args=(str(host), port))
                    t.daemon = True
                    t.start()
                    threads.append(t)

            for t in threads:
                t.join(timeout=0.4)

            if callback:
                callback(detected)

        threading.Thread(target=run_scan, daemon=True).start()

    def build_rdp_command(self, host, port=3389, username="", password="", 
                          fullscreen=False, clipboard=True, sound=True, dynamic_res=True):
        """Constructs RDP command line arguments for FreeRDP or Windows mstsc."""
        if sys.platform == "win32":
            mstsc_bin = shutil.which("mstsc") or r"C:\Windows\System32\mstsc.exe"
            cmd = [mstsc_bin, f"/v:{host}:{port}"]
            if fullscreen:
                cmd.append("/f")
            else:
                cmd.extend(["/w:1280", "/h:720"])
            return cmd

        freerdp_bin = shutil.which("xfreerdp") or shutil.which("freerdp") or "xfreerdp"
        cmd = [freerdp_bin, f"/v:{host}:{port}"]

        if username:
            cmd.append(f"/u:{username}")
        if password:
            cmd.append(f"/p:{password}")

        if fullscreen:
            cmd.append("/f")
        else:
            cmd.append("/w:1280")
            cmd.append("/h:720")

        if clipboard:
            cmd.append("+clipboard")

        if sound:
            cmd.append("/sound:sys:pulse")

        if dynamic_res:
            cmd.append("/dynamic-resolution")

        # Certificate auto-accept for seamless connection
        cmd.append("/cert-ignore")

        return cmd

    def build_spice_command(self, host, port=5900, password="", fullscreen=False):
        """Constructs SPICE client (spicy / remote-viewer) command line arguments."""
        spicy_bin = shutil.which("remote-viewer") or shutil.which("spicy") or "spicy"
        
        if "remote-viewer" in spicy_bin:
            url = f"spice://{host}:{port}"
            cmd = [spicy_bin, url]
            if fullscreen:
                cmd.append("--full-screen")
        else:
            cmd = [spicy_bin, f"-h", host, f"-p", str(port)]
            if password:
                cmd.extend(["-w", password])
            if fullscreen:
                cmd.append("-f")

        return cmd

    def build_vnc_command(self, host, port=5900, fullscreen=False):
        """Constructs VNC client command line arguments."""
        vnc_bin = shutil.which("vncviewer") or "vncviewer"
        cmd = [vnc_bin, f"{host}:{port}"]
        if fullscreen:
            cmd.append("-FullScreen")

        return cmd

    def start_remote_session(self, protocol="rdp", host="127.0.0.1", port=None,
                             username="", password="", fullscreen=False,
                             clipboard=True, sound=True, dynamic_res=True):
        """Launches the selected remote desktop client process asynchronously."""
        if self.is_running:
            self.log_callback("Error: Remote connection is already active.")
            return False

        proto = protocol.lower()
        port = port or (3389 if proto == "rdp" else 5900)

        deps = self.check_remote_dependencies()
        if proto == "rdp" and not deps["has_rdp"]:
            self.log_callback("Error: xfreerdp client is not installed.")
            self.log_callback(f"Run: {deps['install_cmd']}")
            return False
        elif proto == "spice" and not deps["has_spice"]:
            self.log_callback("Error: spicy / remote-viewer client is not installed.")
            self.log_callback(f"Run: {deps['install_cmd']}")
            return False
        elif proto == "vnc" and not deps["has_vnc"]:
            self.log_callback("Error: vncviewer client is not installed.")
            self.log_callback(f"Run: {deps['install_cmd']}")
            return False

        if proto == "rdp":
            full_cmd = self.build_rdp_command(
                host=host, port=port, username=username, password=password,
                fullscreen=fullscreen, clipboard=clipboard, sound=sound, dynamic_res=dynamic_res
            )
        elif proto == "spice":
            full_cmd = self.build_spice_command(
                host=host, port=port, password=password, fullscreen=fullscreen
            )
        else:
            full_cmd = self.build_vnc_command(
                host=host, port=port, fullscreen=fullscreen
            )

        cmd_str = " ".join(full_cmd)
        self.log_callback(f"Initiating {proto.upper()} remote connection to {host}:{port}...\nCommand: {cmd_str}")

        def run_thread():
            try:
                self.process = subprocess.Popen(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    bufsize=1
                )
                self.is_running = True
                self.status_callback("RUNNING")

                def read_stream(stream, prefix):
                    for line in iter(stream.readline, ''):
                        if line:
                            self.log_callback(f"[{prefix}] {line.strip()}")
                    stream.close()

                t_out = threading.Thread(target=read_stream, args=(self.process.stdout, "REMOTE-OUT"))
                t_err = threading.Thread(target=read_stream, args=(self.process.stderr, "REMOTE-ERR"))
                t_out.daemon = True
                t_err.daemon = True
                t_out.start()
                t_err.start()

                self.process.wait()
                rc = self.process.returncode
                self.is_running = False
                self.status_callback("STOPPED")
                self.log_callback(f"Remote connection process exited with return code: {rc}")

            except Exception as e:
                self.is_running = False
                self.status_callback("ERROR")
                self.log_callback(f"Failed to launch remote connection process: {str(e)}")

        self.monitor_thread = threading.Thread(target=run_thread, daemon=True)
        self.monitor_thread.start()
        return True

    def stop_remote_session(self):
        """Terminates active remote desktop connection process."""
        if not self.process or not self.is_running:
            self.log_callback("No active remote connection to stop.")
            return True

        self.log_callback("Disconnecting remote desktop session...")
        try:
            self.process.terminate()
            time.sleep(0.5)
            if self.process.poll() is None:
                self.process.kill()
            self.is_running = False
            self.status_callback("STOPPED")
            return True
        except Exception as e:
            self.log_callback(f"Error stopping remote session: {e}")
            return False
