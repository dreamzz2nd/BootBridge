import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from core.remote_launcher import RemoteLauncher
from ui.components import make_card_header, make_icon_button, set_button_state

class RemotePage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.detected_devices = []
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
        # 1. Network Auto-Scan & Device Picker Card
        # ----------------------------------------------------
        self.scan_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.scan_card.get_style_context().add_class("card")

        scan_hdr, self.scan_title_lbl = make_card_header("network-wireless-symbolic", app.tr("remote_scan_title"))
        self.scan_card.pack_start(scan_hdr, False, False, 0)

        scan_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
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

        scan_row.pack_start(self.scan_combo, True, True, 0)
        scan_row.pack_start(self.scan_btn, False, False, 0)
        self.scan_card.pack_start(scan_row, False, False, 0)

        self.box.pack_start(self.scan_card, False, False, 0)

        # ----------------------------------------------------
        # 2. Remote Connection Config Card
        # ----------------------------------------------------
        self.config_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.config_card.get_style_context().add_class("card")

        hdr_box, self.card_title_lbl = make_card_header("network-workgroup-symbolic", app.tr("remote_card_title"))
        self.config_card.pack_start(hdr_box, False, False, 0)

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
        self.config_card.pack_start(proto_box, False, False, 0)

        # Host IP & Port
        host_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.host_lbl = Gtk.Label(label=app.tr("remote_host"))
        self.host_lbl.set_xalign(0)
        self.host_lbl.set_size_request(130, -1)

        self.host_entry = Gtk.Entry()
        self.host_entry.set_placeholder_text("192.168.1.100 atau hostname.local")
        self.host_entry.set_text("127.0.0.1")

        self.port_lbl = Gtk.Label(label=app.tr("remote_port"))
        self.port_entry = Gtk.Entry()
        self.port_entry.set_width_chars(6)
        self.port_entry.set_text("3389")

        host_box.pack_start(self.host_lbl, False, False, 0)
        host_box.pack_start(self.host_entry, True, True, 0)
        host_box.pack_start(self.port_lbl, False, False, 4)
        host_box.pack_start(self.port_entry, False, False, 0)
        self.config_card.pack_start(host_box, False, False, 0)

        # Credentials (Username & Password)
        cred_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        self.user_lbl = Gtk.Label(label=app.tr("remote_user"))
        self.user_lbl.set_xalign(0)
        self.user_lbl.set_size_request(130, -1)

        self.user_entry = Gtk.Entry()
        self.user_entry.set_placeholder_text("Username Windows (opsional)")

        self.pass_lbl = Gtk.Label(label=app.tr("remote_pass"))
        self.pass_entry = Gtk.Entry()
        self.pass_entry.set_visibility(False)
        self.pass_entry.set_placeholder_text("Password")

        cred_box.pack_start(self.user_lbl, False, False, 0)
        cred_box.pack_start(self.user_entry, True, True, 0)
        cred_box.pack_start(self.pass_lbl, False, False, 4)
        cred_box.pack_start(self.pass_entry, True, True, 0)
        self.config_card.pack_start(cred_box, False, False, 0)

        self.box.pack_start(self.config_card, False, False, 0)

        # ----------------------------------------------------
        # 3. Performance & Display Options Card
        # ----------------------------------------------------
        self.opts_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.opts_card.get_style_context().add_class("card")

        opts_hdr_box, self.opts_title_lbl = make_card_header("preferences-system-symbolic", app.tr("remote_options_title"))
        self.opts_card.pack_start(opts_hdr_box, False, False, 0)

        self.fullscreen_chk = Gtk.CheckButton(label=app.tr("remote_fullscreen_chk"))
        self.fullscreen_chk.set_active(False)

        self.clip_chk = Gtk.CheckButton(label=app.tr("remote_clip_chk"))
        self.clip_chk.set_active(True)

        self.sound_chk = Gtk.CheckButton(label=app.tr("remote_audio_chk"))
        self.sound_chk.set_active(True)

        self.dynres_chk = Gtk.CheckButton(label=app.tr("remote_dynres_chk"))
        self.dynres_chk.set_active(True)

        self.opts_card.pack_start(self.fullscreen_chk, False, False, 0)
        self.opts_card.pack_start(self.clip_chk, False, False, 0)
        self.opts_card.pack_start(self.sound_chk, False, False, 0)
        self.opts_card.pack_start(self.dynres_chk, False, False, 0)
        self.box.pack_start(self.opts_card, False, False, 0)

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

        # Check initial dependencies
        self.update_dependency_status()

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

    def on_scan_clicked(self, widget):
        self.scan_btn.set_sensitive(False)
        self.scan_btn_lbl.set_text(self.app.tr("remote_scanning"))
        self.app.log_message("Scanning local network for active Windows PCs...")

        def on_results(results):
            def update_ui():
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
        elif proto == "spice":
            self.port_entry.set_text("5900")
            self.user_entry.set_sensitive(False)
            self.pass_entry.set_sensitive(True)
            self.sound_chk.set_sensitive(True)
            self.dynres_chk.set_sensitive(False)
        else: # VNC
            self.port_entry.set_text("5900")
            self.user_entry.set_sensitive(False)
            self.pass_entry.set_sensitive(False)
            self.sound_chk.set_sensitive(False)
            self.dynres_chk.set_sensitive(False)

    def apply_language(self):
        self.dep_title_lbl.set_text(self.app.tr("remote_dep_title"))
        self.install_dep_btn_lbl.set_text(self.app.tr("install_remote_dep_btn"))
        self.scan_title_lbl.set_text(self.app.tr("remote_scan_title"))
        self.scan_btn_lbl.set_text(self.app.tr("remote_scan_btn"))
        self.card_title_lbl.set_text(self.app.tr("remote_card_title"))
        self.proto_lbl.set_text(self.app.tr("remote_proto"))
        self.host_lbl.set_text(self.app.tr("remote_host"))
        self.port_lbl.set_text(self.app.tr("remote_port"))
        self.user_lbl.set_text(self.app.tr("remote_user"))
        self.pass_lbl.set_text(self.app.tr("remote_pass"))
        self.opts_title_lbl.set_text(self.app.tr("remote_options_title"))
        self.fullscreen_chk.set_label(self.app.tr("remote_fullscreen_chk"))
        self.clip_chk.set_label(self.app.tr("remote_clip_chk"))
        self.sound_chk.set_label(self.app.tr("remote_audio_chk"))
        self.dynres_chk.set_label(self.app.tr("remote_dynres_chk"))
        self.connect_btn_lbl.set_text(self.app.tr("connect_remote_btn"))
        self.disconnect_btn_lbl.set_text(self.app.tr("disconnect_remote_btn"))
        self.guide_title_lbl.set_text(self.app.tr("remote_guide_title"))
        self.guide_lbl.set_markup(self.app.tr("remote_guide_markup"))
        self.update_dependency_status()
