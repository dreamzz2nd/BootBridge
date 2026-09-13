import socket
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib

from core.remote_launcher import RemoteLauncher
from core.config import load_config
from ui.components import make_card_header, make_icon_button, set_button_state

class RemotePage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.detected_devices = []
        self.current_mode = "easy"  # "easy" or "advanced"
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.box.set_margin_top(16)
        self.box.set_margin_bottom(16)
        self.box.set_margin_start(16)
        self.box.set_margin_end(16)
        self.add(self.box)

        # ----------------------------------------------------
        # 0. Missing Dependency Installer Card (1-Click Install)
        # ----------------------------------------------------
        self.dep_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.dep_card.get_style_context().add_class("card")

        dep_hdr, self.dep_title_lbl = make_card_header("dialog-warning-symbolic", app.tr("remote_dep_title"))
        self.dep_card.pack_start(dep_hdr, False, False, 0)

        self.dep_lbl = Gtk.Label()
        self.dep_lbl.set_xalign(0)
        self.dep_lbl.set_line_wrap(True)
        self.dep_card.pack_start(self.dep_lbl, False, False, 0)

        dep_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.install_dep_btn, self.install_dep_btn_lbl = make_icon_button(
            "system-software-install-symbolic",
            app.tr("install_remote_dep_btn"),
            style_class="btn-primary"
        )
        self.install_dep_btn.connect("clicked", self.on_install_dep_clicked)
        dep_btn_box.pack_start(self.install_dep_btn, False, False, 0)
        self.dep_card.pack_start(dep_btn_box, False, False, 0)

        self.box.pack_start(self.dep_card, False, False, 0)

        # ----------------------------------------------------
        # 1. Mode Switcher Top Bar (Mode Sederhana vs Mode Lanjutan)
        # ----------------------------------------------------
        mode_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        mode_box.set_homogeneous(True)

        self.easy_mode_btn = Gtk.Button(label=app.tr("remote_mode_easy"))
        self.easy_mode_btn.get_style_context().add_class("btn-primary")
        self.easy_mode_btn.connect("clicked", lambda w: self.set_mode("easy"))

        self.adv_mode_btn = Gtk.Button(label=app.tr("remote_mode_adv"))
        self.adv_mode_btn.connect("clicked", lambda w: self.set_mode("advanced"))

        mode_box.pack_start(self.easy_mode_btn, True, True, 0)
        mode_box.pack_start(self.adv_mode_btn, True, True, 0)
        self.box.pack_start(mode_box, False, False, 0)

        # ----------------------------------------------------
        # 2. Easy Mode Card (Target presets, Auto-Scan, Host, Creds, Guide)
        # ----------------------------------------------------
        self.easy_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.easy_card.get_style_context().add_class("card")

        easy_hdr, self.easy_title_lbl = make_card_header("emblem-system-symbolic", app.tr("remote_mode_easy"))
        self.easy_card.pack_start(easy_hdr, False, False, 0)

        # BootBridge "My Computer ID" Banner
        my_id_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        my_id_hdr = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        
        self.my_id_title_lbl = Gtk.Label()
        self.my_id_title_lbl.set_markup(f"<b>{app.tr('remote_my_id_title')}</b>")
        self.my_id_title_lbl.set_xalign(0)

        self.my_id_val_lbl = Gtk.Label()
        local_ip = self._get_local_ip()
        self.my_id_val_lbl.set_markup(f"<span size='x-large' weight='bold' foreground='#3584e4'>{local_ip}</span>")
        self.my_id_val_lbl.set_xalign(0)

        my_id_hdr.pack_start(self.my_id_title_lbl, False, False, 0)
        my_id_hdr.pack_start(self.my_id_val_lbl, False, False, 0)

        self.copy_id_btn, self.copy_id_btn_lbl = make_icon_button(
            "edit-copy-symbolic",
            app.tr("remote_copy_id_btn"),
            style_class="btn-secondary"
        )
        self.copy_id_btn.connect("clicked", self.on_copy_my_id_clicked)

        my_id_card.pack_start(my_id_hdr, True, True, 0)
        my_id_card.pack_start(self.copy_id_btn, False, False, 0)
        self.easy_card.pack_start(my_id_card, False, False, 0)

        # Target Preset (Windows PC vs VM)
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.preset_lbl = Gtk.Label(label=app.tr("remote_target_preset"))
        self.preset_lbl.set_xalign(0)
        self.preset_lbl.set_size_request(180, -1)

        self.preset_combo = Gtk.ComboBoxText()
        self.preset_combo.append("win", app.tr("remote_preset_win"))
        self.preset_combo.append("vm", app.tr("remote_preset_vm"))
        self.preset_combo.set_active_id("win")
        self.preset_combo.connect("changed", self.on_preset_changed)

        preset_box.pack_start(self.preset_lbl, False, False, 0)
        preset_box.pack_start(self.preset_combo, True, True, 0)
        self.easy_card.pack_start(preset_box, False, False, 0)

        # Network Auto-Scan Row
        scan_hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.scan_title_lbl = Gtk.Label(label=app.tr("remote_scan_title"))
        self.scan_title_lbl.set_xalign(0)
        self.scan_title_lbl.set_size_request(180, -1)

        scan_controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.scan_combo = Gtk.ComboBoxText()
        self.scan_combo.append("none", app.tr("remote_scan_placeholder"))
        self.scan_combo.set_active_id("none")
        self.scan_combo.connect("changed", self.on_device_selected)

        self.scan_btn, self.scan_btn_lbl = make_icon_button(
            "view-refresh-symbolic",
            app.tr("remote_scan_btn"),
            style_class="btn-warning"
        )
        self.scan_btn.connect("clicked", self.on_scan_clicked)

        scan_controls.pack_start(self.scan_combo, True, True, 0)
        scan_controls.pack_start(self.scan_btn, False, False, 0)

        scan_hdr_box.pack_start(self.scan_title_lbl, False, False, 0)
        scan_hdr_box.pack_start(scan_controls, True, True, 0)
        self.easy_card.pack_start(scan_hdr_box, False, False, 0)

        # Recent History Dropdown (Quick Reconnect)
        self.history_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.history_lbl = Gtk.Label(label=app.tr("remote_history_lbl"))
        self.history_lbl.set_xalign(0)
        self.history_lbl.set_size_request(180, -1)

        self.history_combo = Gtk.ComboBoxText()
        self.history_combo.connect("changed", self.on_history_selected)

        self.history_box.pack_start(self.history_lbl, False, False, 0)
        self.history_box.pack_start(self.history_combo, True, True, 0)
        self.easy_card.pack_start(self.history_box, False, False, 0)

        # Host / IP Entry
        host_easy_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.host_easy_lbl = Gtk.Label(label=app.tr("remote_easy_host"))
        self.host_easy_lbl.set_xalign(0)
        self.host_easy_lbl.set_size_request(180, -1)

        self.host_easy_entry = Gtk.Entry()
        self.host_easy_entry.set_placeholder_text(app.tr("remote_easy_host_placeholder"))
        self.host_easy_entry.set_text("127.0.0.1")
        self.host_easy_entry.connect("changed", lambda e: self.sync_inputs("easy"))

        host_easy_box.pack_start(self.host_easy_lbl, False, False, 0)
        host_easy_box.pack_start(self.host_easy_entry, True, True, 0)
        self.easy_card.pack_start(host_easy_box, False, False, 0)

        # Credentials Row
        cred_easy_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.user_easy_lbl = Gtk.Label(label=app.tr("remote_user"))
        self.user_easy_lbl.set_xalign(0)
        self.user_easy_lbl.set_size_request(180, -1)

        self.user_easy_entry = Gtk.Entry()
        self.user_easy_entry.set_placeholder_text(app.tr("remote_easy_user_placeholder"))
        self.user_easy_entry.connect("changed", lambda e: self.sync_inputs("easy"))

        self.pass_easy_lbl = Gtk.Label(label=app.tr("remote_pass"))
        self.pass_easy_entry = Gtk.Entry()
        self.pass_easy_entry.set_visibility(False)
        self.pass_easy_entry.set_placeholder_text(app.tr("remote_easy_pass_placeholder"))
        self.pass_easy_entry.connect("changed", lambda e: self.sync_inputs("easy"))

        cred_easy_box.pack_start(self.user_easy_lbl, False, False, 0)
        cred_easy_box.pack_start(self.user_easy_entry, True, True, 0)
        cred_easy_box.pack_start(self.pass_easy_lbl, False, False, 4)
        cred_easy_box.pack_start(self.pass_easy_entry, True, True, 0)
        self.easy_card.pack_start(cred_easy_box, False, False, 0)

        # 1-Click Interactive Guide Button
        guide_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.guide_win_btn, self.guide_win_btn_lbl = make_icon_button(
            "help-about-symbolic",
            app.tr("remote_guide_win_btn"),
            style_class="btn-secondary"
        )
        self.guide_win_btn.connect("clicked", self._show_windows_setup_guide_dialog)
        guide_btn_box.pack_start(self.guide_win_btn, True, True, 0)
        self.easy_card.pack_start(guide_btn_box, False, False, 0)

        self.box.pack_start(self.easy_card, False, False, 0)

        # ----------------------------------------------------
        # 3. Advanced Mode Card (Full protocol & options controls)
        # ----------------------------------------------------
        self.adv_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.adv_card.get_style_context().add_class("card")

        adv_hdr_box, self.adv_card_title_lbl = make_card_header("network-workgroup-symbolic", app.tr("remote_card_title"))
        self.adv_card.pack_start(adv_hdr_box, False, False, 0)

        # Protocol Selector
        proto_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.proto_lbl = Gtk.Label(label=app.tr("remote_proto"))
        self.proto_lbl.set_xalign(0)
        self.proto_lbl.set_size_request(130, -1)

        self.proto_combo = Gtk.ComboBoxText()
        self.proto_combo.append("rdp", "RDP - Windows Remote Desktop (Port 3389)")
        self.proto_combo.append("spice", "SPICE - Remote Virtual Machine (Port 5900)")
        self.proto_combo.append("vnc", "VNC - Universal Desktop Connection (Port 5900)")
        self.proto_combo.set_active_id("rdp")
        self.proto_combo.connect("changed", self.on_protocol_changed)

        proto_box.pack_start(self.proto_lbl, False, False, 0)
        proto_box.pack_start(self.proto_combo, True, True, 0)
        self.adv_card.pack_start(proto_box, False, False, 0)

        # Host IP & Port
        host_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.host_lbl = Gtk.Label(label=app.tr("remote_host"))
        self.host_lbl.set_xalign(0)
        self.host_lbl.set_size_request(130, -1)

        self.host_entry = Gtk.Entry()
        self.host_entry.set_placeholder_text("192.168.1.100 atau hostname.local")
        self.host_entry.set_text("127.0.0.1")
        self.host_entry.connect("changed", lambda e: self.sync_inputs("advanced"))

        self.port_lbl = Gtk.Label(label=app.tr("remote_port"))
        self.port_entry = Gtk.Entry()
        self.port_entry.set_width_chars(6)
        self.port_entry.set_text("3389")

        host_box.pack_start(self.host_lbl, False, False, 0)
        host_box.pack_start(self.host_entry, True, True, 0)
        host_box.pack_start(self.port_lbl, False, False, 4)
        host_box.pack_start(self.port_entry, False, False, 0)
        self.adv_card.pack_start(host_box, False, False, 0)

        # Credentials (Username & Password)
        cred_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.user_lbl = Gtk.Label(label=app.tr("remote_user"))
        self.user_lbl.set_xalign(0)
        self.user_lbl.set_size_request(130, -1)

        self.user_entry = Gtk.Entry()
        self.user_entry.set_placeholder_text("Username Windows (opsional)")
        self.user_entry.connect("changed", lambda e: self.sync_inputs("advanced"))

        self.pass_lbl = Gtk.Label(label=app.tr("remote_pass"))
        self.pass_entry = Gtk.Entry()
        self.pass_entry.set_visibility(False)
        self.pass_entry.set_placeholder_text("Password")
        self.pass_entry.connect("changed", lambda e: self.sync_inputs("advanced"))

        cred_box.pack_start(self.user_lbl, False, False, 0)
        cred_box.pack_start(self.user_entry, True, True, 0)
        cred_box.pack_start(self.pass_lbl, False, False, 4)
        cred_box.pack_start(self.pass_entry, True, True, 0)
        self.adv_card.pack_start(cred_box, False, False, 0)

        # Options Checkboxes
        self.fullscreen_chk = Gtk.CheckButton(label=app.tr("remote_fullscreen_chk"))
        self.fullscreen_chk.set_active(False)

        self.clip_chk = Gtk.CheckButton(label=app.tr("remote_clip_chk"))
        self.clip_chk.set_active(True)

        self.sound_chk = Gtk.CheckButton(label=app.tr("remote_audio_chk"))
        self.sound_chk.set_active(True)

        self.dynres_chk = Gtk.CheckButton(label=app.tr("remote_dynres_chk"))
        self.dynres_chk.set_active(True)

        self.adv_card.pack_start(self.fullscreen_chk, False, False, 0)
        self.adv_card.pack_start(self.clip_chk, False, False, 0)
        self.adv_card.pack_start(self.sound_chk, False, False, 0)
        self.adv_card.pack_start(self.dynres_chk, False, False, 0)

        self.box.pack_start(self.adv_card, False, False, 0)
        self.adv_card.hide()  # Easy mode active by default

        # ----------------------------------------------------
        # 4. Action Buttons Card (Connect / Disconnect)
        # ----------------------------------------------------
        self.action_card = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.action_card.get_style_context().add_class("card")

        self.connect_btn, self.connect_btn_lbl = make_icon_button(
            "network-workgroup-symbolic",
            app.tr("connect_remote_btn"),
            style_class="btn-primary"
        )
        self.connect_btn.connect("clicked", app.on_connect_remote_clicked)

        self.disconnect_btn, self.disconnect_btn_lbl = make_icon_button(
            "process-stop-symbolic",
            app.tr("disconnect_remote_btn"),
            style_class="btn-danger"
        )
        self.disconnect_btn.set_sensitive(False)
        self.disconnect_btn.connect("clicked", app.on_disconnect_remote_clicked)

        self.action_card.pack_start(self.connect_btn, True, True, 0)
        self.action_card.pack_start(self.disconnect_btn, True, True, 0)
        self.box.pack_start(self.action_card, False, False, 0)

        # ----------------------------------------------------
        # 5. Beginners Quick Guidance Card
        # ----------------------------------------------------
        self.guide_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.guide_card.get_style_context().add_class("card")

        guide_hdr, self.guide_title_lbl = make_card_header("help-faq-symbolic", app.tr("remote_guide_title"))
        self.guide_card.pack_start(guide_hdr, False, False, 0)

        self.guide_lbl = Gtk.Label()
        self.guide_lbl.set_xalign(0)
        self.guide_lbl.set_line_wrap(True)
        self.guide_lbl.set_markup(app.tr("remote_guide_markup"))
        self.guide_card.pack_start(self.guide_lbl, False, False, 0)
        self.box.pack_start(self.guide_card, False, False, 0)

        # Refresh history dropdown & initial dependencies
        self.refresh_history()
        self.update_dependency_status()

        # Trigger initial network auto-scan in background
        GLib.timeout_add(1000, lambda: self.on_scan_clicked(None) or False)

    def set_mode(self, mode):
        self.current_mode = mode
        if mode == "easy":
            self.easy_mode_btn.get_style_context().add_class("btn-primary")
            self.adv_mode_btn.get_style_context().remove_class("btn-primary")
            self.easy_card.show_all()
            self.adv_card.hide()
            self.refresh_history()
        else:
            self.adv_mode_btn.get_style_context().add_class("btn-primary")
            self.easy_mode_btn.get_style_context().remove_class("btn-primary")
            self.easy_card.hide()
            self.adv_card.show_all()

    def sync_inputs(self, source):
        if source == "easy":
            text_host = self.host_easy_entry.get_text()
            text_user = self.user_easy_entry.get_text()
            text_pass = self.pass_easy_entry.get_text()
            if self.host_entry.get_text() != text_host:
                self.host_entry.set_text(text_host)
            if self.user_entry.get_text() != text_user:
                self.user_entry.set_text(text_user)
            if self.pass_entry.get_text() != text_pass:
                self.pass_entry.set_text(text_pass)
        else:
            text_host = self.host_entry.get_text()
            text_user = self.user_entry.get_text()
            text_pass = self.pass_entry.get_text()
            if self.host_easy_entry.get_text() != text_host:
                self.host_easy_entry.set_text(text_host)
            if self.user_easy_entry.get_text() != text_user:
                self.user_easy_entry.set_text(text_user)
            if self.pass_easy_entry.get_text() != text_pass:
                self.pass_easy_entry.set_text(text_pass)

    def on_preset_changed(self, combo):
        preset = combo.get_active_id()
        if preset == "win":
            self.proto_combo.set_active_id("rdp")
        else:
            self.proto_combo.set_active_id("spice")

    def refresh_history(self):
        cfg = load_config()
        history = cfg.get("remote_history", [])
        self.history_combo.remove_all()

        if not history:
            self.history_box.hide()
        else:
            self.history_box.show_all()
            self.history_combo.append("none", self.app.tr("remote_history_empty"))
            for idx, item in enumerate(history):
                label = f"{item.get('host')} ({item.get('proto', 'RDP').upper()})"
                if item.get('user'):
                    label += f" - User: {item.get('user')}"
                self.history_combo.append(str(idx), label)
            self.history_combo.set_active_id("none")

    def on_history_selected(self, combo):
        active_id = combo.get_active_id()
        if active_id and active_id.isdigit():
            cfg = load_config()
            history = cfg.get("remote_history", [])
            idx = int(active_id)
            if 0 <= idx < len(history):
                item = history[idx]
                self.host_easy_entry.set_text(item.get("host", "127.0.0.1"))
                self.user_easy_entry.set_text(item.get("user", ""))
                self.proto_combo.set_active_id(item.get("proto", "rdp"))
                if item.get("port"):
                    self.port_entry.set_text(str(item.get("port")))

    def update_dependency_status(self):
        deps = RemoteLauncher.check_remote_dependencies()
        if not deps["has_rdp"] and not deps["has_spice"]:
            self.dep_lbl.set_markup(self.app.tr("remote_dep_msg", cmd=deps["install_cmd"]))
            self.dep_card.show_all()
        else:
            self.dep_card.hide()

    def on_install_dep_clicked(self, widget):
        self.install_dep_btn.set_sensitive(False)
        def run_installer():
            success, msg = RemoteLauncher.install_remote_dependencies(log_callback=self.app.log_message)
            def update_ui():
                self.install_dep_btn.set_sensitive(True)
                self.update_dependency_status()
            GLib.idle_add(update_ui)
        import threading
        threading.Thread(target=run_installer, daemon=True).start()

    def on_scan_clicked(self, widget=None):
        if widget:
            self.scan_btn.set_sensitive(False)
            self.scan_btn_lbl.set_text(self.app.tr("remote_scanning"))
        self.app.log_message("Scanning local network for active Windows PCs...")

        def on_results(results):
            def update_ui():
                if widget:
                    self.scan_btn.set_sensitive(True)
                    self.scan_btn_lbl.set_text(self.app.tr("remote_scan_btn"))
                self.detected_devices = results
                self.scan_combo.remove_all()

                if not results:
                    self.scan_combo.append("none", self.app.tr("remote_no_devices_found"))
                    self.scan_combo.set_active_id("none")
                    self.app.log_message("Network scan complete: No active remote devices found.")
                else:
                    self.scan_combo.append("none", self.app.tr("remote_select_detected"))
                    for idx, dev in enumerate(results):
                        self.scan_combo.append(str(idx), dev["label"])
                    self.scan_combo.set_active(0)
                    self.app.log_message(f"Network scan complete: Found {len(results)} remote device(s)!")

            GLib.idle_add(update_ui)

        RemoteLauncher.scan_local_network(callback=on_results)

    def on_device_selected(self, combo):
        active_id = combo.get_active_id()
        if active_id and active_id.isdigit():
            idx = int(active_id)
            if 0 <= idx < len(self.detected_devices):
                dev = self.detected_devices[idx]
                self.host_easy_entry.set_text(dev["host"])
                self.host_entry.set_text(dev["host"])
                self.port_entry.set_text(str(dev["port"]))
                self.proto_combo.set_active_id(dev["proto"])

    def on_protocol_changed(self, combo):
        proto = combo.get_active_id()
        if proto == "rdp":
            self.port_entry.set_text("3389")
            self.user_entry.set_sensitive(True)
            self.pass_entry.set_sensitive(True)
            self.sound_chk.set_sensitive(True)
            self.dynres_chk.set_sensitive(True)
            self.preset_combo.set_active_id("win")
        elif proto == "spice":
            self.port_entry.set_text("5900")
            self.user_entry.set_sensitive(False)
            self.pass_entry.set_sensitive(True)
            self.sound_chk.set_sensitive(True)
            self.dynres_chk.set_sensitive(False)
            self.preset_combo.set_active_id("vm")
        else: # VNC
            self.port_entry.set_text("5900")
            self.user_entry.set_sensitive(False)
            self.pass_entry.set_sensitive(False)
            self.sound_chk.set_sensitive(False)
            self.dynres_chk.set_sensitive(False)

    def _show_windows_setup_guide_dialog(self, widget=None):
        dialog = Gtk.Dialog(
            title=self.app.tr("remote_guide_dialog_title"),
            transient_for=self.app,
            flags=0
        )
        dialog.set_modal(True)
        dialog.set_default_size(520, -1)

        box = dialog.get_content_area()
        box.set_spacing(12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        icon = Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.DND)
        lbl_hdr = Gtk.Label()
        lbl_hdr.set_markup(f"<b><big>{GLib.markup_escape_text(self.app.tr('remote_guide_dialog_title'))}</big></b>")
        hdr_box.pack_start(icon, False, False, 0)
        hdr_box.pack_start(lbl_hdr, False, False, 0)
        box.pack_start(hdr_box, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sep, False, False, 0)

        body_lbl = Gtk.Label()
        body_lbl.set_xalign(0)
        body_lbl.set_line_wrap(True)
        body_lbl.set_markup(self.app.tr("remote_guide_dialog_markup"))
        box.pack_start(body_lbl, False, False, 0)

        dialog.add_button("Mengerti", Gtk.ResponseType.OK)
        box.show_all()
        dialog.run()
        dialog.destroy()

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def on_copy_my_id_clicked(self, widget):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(self._get_local_ip(), -1)
        self.app.set_status("ID / Alamat IP Komputer Ini disalin ke clipboard!")

    def apply_language(self):
        self.dep_title_lbl.set_text(self.app.tr("remote_dep_title"))
        self.install_dep_btn_lbl.set_text(self.app.tr("install_remote_dep_btn"))
        self.easy_mode_btn.set_label(self.app.tr("remote_mode_easy"))
        self.adv_mode_btn.set_label(self.app.tr("remote_mode_adv"))
        self.easy_title_lbl.set_text(self.app.tr("remote_mode_easy"))
        self.my_id_title_lbl.set_markup(f"<b>{self.app.tr('remote_my_id_title')}</b>")
        self.copy_id_btn_lbl.set_text(self.app.tr("remote_copy_id_btn"))
        self.preset_lbl.set_text(self.app.tr("remote_target_preset"))
        self.scan_title_lbl.set_text(self.app.tr("remote_scan_title"))
        self.scan_btn_lbl.set_text(self.app.tr("remote_scan_btn"))
        self.history_lbl.set_text(self.app.tr("remote_history_lbl"))
        self.host_easy_lbl.set_text(self.app.tr("remote_easy_host"))
        self.user_easy_lbl.set_text(self.app.tr("remote_user"))
        self.pass_easy_lbl.set_text(self.app.tr("remote_pass"))
        self.guide_win_btn_lbl.set_text(self.app.tr("remote_guide_win_btn"))

        self.adv_card_title_lbl.set_text(self.app.tr("remote_card_title"))
        self.proto_lbl.set_text(self.app.tr("remote_proto"))
        self.host_lbl.set_text(self.app.tr("remote_host"))
        self.port_lbl.set_text(self.app.tr("remote_port"))
        self.user_lbl.set_text(self.app.tr("remote_user"))
        self.pass_lbl.set_text(self.app.tr("remote_pass"))
        self.fullscreen_chk.set_label(self.app.tr("remote_fullscreen_chk"))
        self.clip_chk.set_label(self.app.tr("remote_clip_chk"))
        self.sound_chk.set_label(self.app.tr("remote_audio_chk"))
        self.dynres_chk.set_label(self.app.tr("remote_dynres_chk"))
        self.connect_btn_lbl.set_text(self.app.tr("connect_remote_btn"))
        self.disconnect_btn_lbl.set_text(self.app.tr("disconnect_remote_btn"))
        self.guide_title_lbl.set_text(self.app.tr("remote_guide_title"))
        self.guide_lbl.set_markup(self.app.tr("remote_guide_markup"))
        self.refresh_history()
        self.update_dependency_status()
