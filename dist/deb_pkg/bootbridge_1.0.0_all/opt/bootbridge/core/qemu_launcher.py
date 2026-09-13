import os
import sys
import subprocess
import threading
import time
import shutil
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.safety_checker import SafetyChecker

class QEMULauncher:
    """Manages QEMU/KVM virtual machine creation, execution, and process control."""

    def __init__(self, log_callback=None, status_callback=None, help_callback=None):
        self.process = None
        self.is_running = False
        self.log_callback = log_callback or (lambda text: print(f"[QEMU] {text}"))
        self.status_callback = status_callback or (lambda status: None)
        self.help_callback = help_callback
        self.monitor_thread = None
        self.vars_copy_path = None

    def _setup_swtpm(self):
        """Launches swtpm daemon in socket mode if swtpm package is installed."""
        if not shutil.which("swtpm"):
            return None
        try:
            tpm_dir = os.path.join(tempfile.gettempdir(), "bootbridge_tpm")
            os.makedirs(tpm_dir, exist_ok=True)
            sock_path = os.path.join(tpm_dir, "swtpm-sock")
            
            subprocess.run(["pkill", "-f", sock_path], capture_output=True)
            time.sleep(0.1)

            swtpm_cmd = [
                "swtpm", "socket",
                "--tpmstate", f"dir={tpm_dir}",
                "--ctrl", f"type=unixio,path={sock_path}",
                "--tpm2"
            ]
            self.swtpm_proc = subprocess.Popen(swtpm_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.2)
            if os.path.exists(sock_path):
                self.log_callback("TPM 2.0 Emulator (swtpm) initialized successfully.")
                return sock_path
        except Exception as e:
            self.log_callback(f"Warning setting up swtpm: {e}")
        return None

    def build_command(self, disk_path, ram_mb=4096, cpu_cores=4, display_type="gtk", 
                      ovmf_code=None, ovmf_vars=None, is_shared_host_disk=False, fullscreen=False,
                      guest_os_type="auto"):
        """
        Constructs the qemu-system-x86_64 command line argument list for Windows, macOS, or Linux Guest.
        """
        deps = SafetyChecker.check_system_dependencies()
        qemu_bin = deps.get("qemu_path") or "qemu-system-x86_64"
        
        ovmf_code = ovmf_code or deps.get("ovmf_code")
        ovmf_vars = ovmf_vars or deps.get("ovmf_vars")

        cmd = [qemu_bin]

        if fullscreen:
            cmd.append("-full-screen")

        is_secboot = bool(ovmf_code and ("secboot" in ovmf_code or "ms.fd" in ovmf_code))

        # Machine & Hypervisor Hardware Acceleration (Linux: KVM, macOS: HVF, Windows: WHPX)
        accel_type = deps.get("accel_type")
        if accel_type == "kvm" or deps.get("kvm_available"):
            if is_secboot:
                cmd.extend(["-enable-kvm", "-machine", "q35,smm=on,accel=kvm", "-global", "driver=cfi.pflash01,property=secure,value=on"])
            else:
                cmd.extend(["-enable-kvm", "-machine", "q35,accel=kvm"])
            
            if guest_os_type == "macos":
                cmd.extend(["-cpu", "Penryn,vendor=GenuineIntel,+ssse3,+sse4.1,+sse4.2,+popcnt,+aes,+xsave,+avx,+xsaveopt,check"])
            elif guest_os_type == "linux":
                cmd.extend(["-cpu", "host"])
            else: # Windows guest default
                cmd.extend([
                    "-cpu", "host,hv_relaxed,hv_spinlocks=0x1fff,hv_vapic,hv_time,hv_synic,hv_stimer,hv_reset,hv_vpindex,hv_runtime,hv_tlbflush,hv_ipi,kvm=on"
                ])
        elif accel_type == "hvf":
            cmd.extend(["-machine", "q35,accel=hvf", "-cpu", "host"])
        elif accel_type == "whpx":
            cmd.extend(["-machine", "q35,accel=whpx", "-cpu", "host"])
        else:
            cmd.extend(["-machine", "q35", "-cpu", "max"])

        cmd.extend(["-smp", f"cores={cpu_cores},threads=1,sockets=1"])

        # RAM Memory
        cmd.extend(["-m", str(ram_mb)])

        # Real-Time Clock (Synchronize Windows clock with local time)
        cmd.extend(["-rtc", "base=localtime,clock=host"])

        # UEFI Firmware (OVMF)
        if ovmf_code and os.path.exists(ovmf_code):
            if "OVMF_CODE" in ovmf_code:
                cmd.extend(["-drive", f"if=pflash,unit=0,format=raw,readonly=on,file={ovmf_code}"])
                if ovmf_vars and os.path.exists(ovmf_vars):
                    try:
                        tmp_dir = tempfile.gettempdir()
                        self.vars_copy_path = os.path.join(tmp_dir, "bootbridge_ovmf_vars.fd")
                        if not os.path.exists(self.vars_copy_path) or os.path.getsize(self.vars_copy_path) == 0:
                            shutil.copyfile(ovmf_vars, self.vars_copy_path)
                        cmd.extend(["-drive", f"if=pflash,unit=1,format=raw,file={self.vars_copy_path}"])
                    except Exception as e:
                        self.log_callback(f"Warning OVMF vars copy failed: {e}")
            else: # Combined single-file OVMF firmware
                cmd.extend(["-bios", ovmf_code])

        # TPM 2.0 (swtpm) emulator integration
        tpm_sock = self._setup_swtpm()
        if tpm_sock:
            cmd.extend([
                "-chardev", f"socket,id=chrtpm,path={tpm_sock}",
                "-tpmdev", "emulator,id=tpm0,chardev=chrtpm",
                "-device", "tpm-tis,tpmdev=tpm0"
            ])

        # Physical Disk Passthrough (Native NVMe device for NVMe SSD, AHCI/SATA for sdX)
        if "nvme" in disk_path.lower():
            cmd.extend([
                "-drive", f"file={disk_path},format=raw,if=none,id=drive0,cache=none,aio=native,discard=unmap",
                "-device", "nvme,drive=drive0,serial=bootbridge_nvme"
            ])
        else:
            cmd.extend([
                "-device", "ahci,id=ahci",
                "-drive", f"file={disk_path},format=raw,if=none,id=drive0,cache=none,aio=native",
                "-device", "ide-hd,bus=ahci.0,drive=drive0"
            ])

        # Bidirectional Host <-> Guest Clipboard Sharing (qemu-vdagent)
        cmd.extend([
            "-chardev", "qemu-vdagent,id=chd,name=vdagent,clipboard=on",
            "-device", "virtio-serial-pci",
            "-device", "virtserialport,chardev=chd,name=com.redhat.spice.0"
        ])

        # VGA Graphics & Display (QXL paravirtual display adapter with auto zoom-to-fit scaling & keyboard grab)
        if display_type == "gtk":
            opts = "gtk,zoom-to-fit=on,show-menubar=off,window-close=off,grab-on-hover=on"
            if fullscreen:
                opts += ",full-screen=on"
            cmd.extend(["-vga", "qxl", "-display", opts])
        elif display_type == "sdl":
            if fullscreen:
                cmd.extend(["-vga", "qxl", "-display", "sdl,zoom-to-fit=on", "-full-screen"])
            else:
                cmd.extend(["-vga", "qxl", "-display", "sdl,zoom-to-fit=on"])
        elif display_type == "spice":
            cmd.extend(["-vga", "qxl", "-spice", "port=5900,disable-ticketing=on", "-display", "none"])
        else: # Default fallback GTK
            opts = "gtk,zoom-to-fit=on,show-menubar=off,window-close=off,grab-on-hover=on"
            if fullscreen:
                opts += ",full-screen=on"
            cmd.extend(["-vga", "qxl", "-display", opts])

        # USB Tablet Pointer (prevents mouse lock inside VM window)
        cmd.extend(["-usb", "-device", "usb-tablet"])

        # Audio (Intel HDA)
        cmd.extend(["-device", "intel-hda", "-device", "hda-duplex"])

        # Network NAT (Intel e1000e network card - built into Windows out-of-the-box)
        cmd.extend(["-netdev", "user,id=net0", "-device", "e1000e,netdev=net0"])

        return cmd

    def start_vm(self, disk_path, ram_mb=4096, cpu_cores=4, display_type="gtk", use_pkexec=True, fullscreen=False):
        """Launches the VM process asynchronously with elevated block device permissions."""
        if self.is_running:
            self.log_callback("Error: VM is already running.")
            return False

        deps = SafetyChecker.check_system_dependencies()
        if not deps.get("qemu_installed"):
            self.log_callback("Error: qemu-system-x86_64 is not installed on system.")
            self.log_callback(f"Run this command to install: {deps.get('install_command')}")
            return False

        # Grant read/write access to physical block device and its partitions if unprivileged
        if use_pkexec and deps.get("pkexec_installed") and not os.access(disk_path, os.W_OK):
            user = os.environ.get("USER") or "rizky"
            self.log_callback(f"Granting device read/write permissions for {disk_path} via pkexec...")
            res = subprocess.run(["pkexec", "setfacl", "-m", f"u:{user}:rw", disk_path], capture_output=True, text=True)
            if res.returncode != 0:
                subprocess.run(["pkexec", "chmod", "a+rw", disk_path], capture_output=True, text=True)
            
            # Apply to matching partitions (e.g. nvme0n1p1, sda1, etc.)
            try:
                parent_dir = os.path.dirname(disk_path)
                base_name = os.path.basename(disk_path)
                for item in os.listdir(parent_dir):
                    if item.startswith(base_name) and item != base_name:
                        part_path = os.path.join(parent_dir, item)
                        subprocess.run(["setfacl", "-m", f"u:{user}:rw", part_path], capture_output=True, text=True)
            except Exception as e:
                self.log_callback(f"Partition ACL notice: {e}")

        full_cmd = self.build_command(
            disk_path=disk_path,
            ram_mb=ram_mb,
            cpu_cores=cpu_cores,
            display_type=display_type,
            fullscreen=fullscreen
        )

        cmd_str = " ".join(full_cmd)
        self.log_callback(f"Launching QEMU VM...\nCommand: {cmd_str}")

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

                # Monitor stderr / stdout streams
                def read_stream(stream, prefix):
                    for line in iter(stream.readline, ''):
                        if line:
                            self.log_callback(f"[{prefix}] {line.strip()}")
                    stream.close()

                t_out = threading.Thread(target=read_stream, args=(self.process.stdout, "QEMU-OUT"))
                t_err = threading.Thread(target=read_stream, args=(self.process.stderr, "QEMU-ERR"))
                t_out.daemon = True
                t_err.daemon = True
                t_out.start()
                t_err.start()

                # Remove window decorations (titlebar and close button) pasca-launch
                threading.Thread(target=self._strip_window_decorations, daemon=True).start()

                # Start global X11 hotkey listener for Ctrl+Alt+H inside VM
                threading.Thread(target=self._start_global_hotkey_listener, daemon=True).start()

                self.process.wait()
                rc = self.process.returncode
                self.is_running = False
                self.status_callback("STOPPED")
                self.log_callback(f"QEMU process exited with return code: {rc}")

            except Exception as e:
                self.is_running = False
                self.status_callback("ERROR")
                self.log_callback(f"Failed to execute QEMU process: {str(e)}")

        self.monitor_thread = threading.Thread(target=run_thread)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        return True

    def _start_global_hotkey_listener(self):
        """Monitors global Ctrl+Alt+H hotkey while VM is running to toggle shortcut guide."""
        try:
            from Xlib import X, display, XK
            disp = display.Display()
            root = disp.screen().root
            keysym = XK.string_to_keysym('h')
            keycode = disp.keysym_to_keycode(keysym)
            if not keycode:
                return

            modifiers = X.ControlMask | X.Mod1Mask
            for numlock_mask in [0, X.Mod2Mask, X.LockMask, X.Mod2Mask | X.LockMask]:
                try:
                    root.grab_key(keycode, modifiers | numlock_mask, True, X.GrabModeAsync, X.GrabModeAsync)
                except Exception:
                    pass
            disp.sync()

            while self.is_running and self.process and self.process.poll() is None:
                if disp.pending_events() > 0:
                    event = disp.next_event()
                    if event.type == X.KeyPress:
                        if self.help_callback:
                            from gi.repository import GLib
                            GLib.idle_add(self.help_callback)
                else:
                    time.sleep(0.1)

            for numlock_mask in [0, X.Mod2Mask, X.LockMask, X.Mod2Mask | X.LockMask]:
                try:
                    root.ungrab_key(keycode, modifiers | numlock_mask)
                except Exception:
                    pass
            disp.close()
        except Exception as e:
            self.log_callback(f"Notice global hotkey listener: {e}")

    def _strip_window_decorations(self):
        """Removes titlebar, frame, and close button from QEMU GTK window using xprop / wmctrl."""
        time.sleep(1.0)
        try:
            res = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
            if res.returncode == 0:
                for line in res.stdout.splitlines():
                    if "qemu" in line.lower():
                        win_id = line.split()[0]
                        subprocess.run(["xprop", "-id", win_id, "-f", "_MOTIF_WM_HINTS", "32c", "-set", "_MOTIF_WM_HINTS", "0x2, 0x0, 0x0, 0x0, 0x0"], capture_output=True)
                        self.log_callback("Removed window titlebar and close button from QEMU display.")
                        break
        except Exception as e:
            self.log_callback(f"Notice stripping window decorations: {e}")

    def stop_vm(self, force=False):
        """Stops the running VM process."""
        if not self.process or not self.is_running:
            self.log_callback("VM is not currently running.")
            return True

        self.log_callback("Stopping Windows VM...")
        try:
            if force:
                self.process.kill()
                self.log_callback("VM forcibly killed.")
            else:
                self.process.terminate()
                # Wait up to 5 seconds for clean exit
                threading.Thread(target=self._wait_and_kill).start()
            return True
        except Exception as e:
            self.log_callback(f"Error stopping VM: {e}")
            return False

    def _wait_and_kill(self):
        time.sleep(5)
        if self.process and self.process.poll() is None:
            self.log_callback("VM process did not terminate gracefully. Forcing kill...")
            try:
                self.process.kill()
            except Exception:
                pass

if __name__ == "__main__":
    launcher = QEMULauncher()
    cmd = launcher.build_command("/dev/nvme0n1", ram_mb=4096, cpu_cores=4)
    print("Generated QEMU Command:")
    print(" ".join(cmd))
