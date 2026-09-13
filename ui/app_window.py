"""
Main GTK Application Window & Event Orchestrator for BootBridge
"""

import os
import sys
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

from core.config import load_config, save_config, add_remote_history
from core.disk_manager import DiskManager
from core.safety_checker import SafetyChecker
from core.qemu_launcher import QEMULauncher
from core.remote_launcher import RemoteLauncher

from ui.i18n import tr, batch_translate_language
from ui.components import make_icon_button, set_button_state
from ui.pages.dashboard_page import DashboardPage
from ui.pages.safety_page import SafetyPage
from ui.pages.hardware_page import HardwarePage
from ui.pages.guides_page import GuidesPage
from ui.pages.diagnostics_page import DiagnosticsPage
from ui.pages.remote_page import RemotePage
from ui.pages.settings_page import SettingsPage

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class BootBridgeApp(Gtk.Window):
    def __init__(self):
        super().__init__(title="BootBridge")
        self.set_default_size(880, 680)
        self.set_position(Gtk.WindowPosition.CENTER)

        # Set Window Icon & WM Class / Prgname
        GLib.set_prgname("bootbridge")
        GLib.set_application_name("BootBridge")
        
        icon_path = os.path.join(BASE_DIR, "assets", "bootbridge.png")
        if os.path.exists(icon_path):
            try:
                Gtk.Window.set_default_icon_from_file(icon_path)
                self.set_icon_from_file(icon_path)
            except Exception as e:
                print(f"[BootBridge] Warning setting window icon: {e}")


        # Load Saved Config & Preferences
        self.config = load_config()
        self.current_lang = self.config.get("language", "id")
        self.current_theme = self.config.get("theme", "dark")
        self.css_provider = None

        # State Variables
        self.disks = []
        self.selected_disk = None
        self.deps = SafetyChecker.check_system_dependencies()
        self.launcher = QEMULauncher(
            log_callback=self.log_message,
            status_callback=self.on_vm_status_changed,
            help_callback=lambda: self._show_launch_guide_dialog(is_manual=True)
        )
        self.remote_launcher = RemoteLauncher(
            log_callback=self.log_message,
            status_callback=self.on_remote_status_changed
        )

        # Load Custom CSS Styling
        self.load_css()

        # Connect Global Application Shortcut Handler (Ctrl + Alt + H)
        self.connect("key-press-event", self.on_key_press_event)

        # Build GUI Layout & Navigation
        self.build_ui()

        # Refresh disk listing & apply language
        self.apply_language()

        if self.current_lang not in ("id", "en"):
            batch_translate_language(self.current_lang, callback=lambda s: GLib.idle_add(self.apply_language))

    def tr(self, key, **kwargs):
        return tr(key, lang=self.current_lang, **kwargs)

    def load_css(self):
        theme = self.config.get("theme", "dark")
        css_filename = "style_dark.css" if theme == "dark" else "style_light.css"
        css_path = os.path.join(BASE_DIR, "assets", css_filename)

        if self.css_provider:
            try:
                Gtk.StyleContext.remove_provider_for_screen(
                    Gdk.Screen.get_default(),
                    self.css_provider
                )
            except Exception:
                pass
        
        self.css_provider = Gtk.CssProvider()
        if os.path.exists(css_path):
            try:
                self.css_provider.load_from_path(css_path)
                Gtk.StyleContext.add_provider_for_screen(
                    Gdk.Screen.get_default(),
                    self.css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
            except Exception as e:
                print(f"[BootBridge] Warning loading CSS ({css_filename}): {e}")

    def build_ui(self):
        # HeaderBar
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "BootBridge"
        self.header.props.subtitle = self.tr("app_subtitle")
        self.set_titlebar(self.header)

        # Refresh Button
        refresh_btn = Gtk.Button()
        refresh_btn.set_tooltip_text("Refresh Physical Disks")
        refresh_icon = Gtk.Image.new_from_icon_name("view-refresh-symbolic", Gtk.IconSize.BUTTON)
        refresh_btn.add(refresh_icon)
        refresh_btn.connect("clicked", lambda x: self.refresh_disks())
        self.header.pack_start(refresh_btn)

        # Main Horizontal Window Box (Sidebar + Main Content Area)
        main_h_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add(main_h_box)

        # ==========================================
        # LEFT NAVIGATION SIDEBAR
        # ==========================================
        sidebar_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        sidebar_container.get_style_context().add_class("sidebar")

        self.sidebar_title_lbl = Gtk.Label(label=self.tr("nav_title"))
        self.sidebar_title_lbl.set_xalign(0)
        self.sidebar_title_lbl.get_style_context().add_class("sidebar-title")
        sidebar_container.pack_start(self.sidebar_title_lbl, False, False, 4)

        self.sidebar_list = Gtk.ListBox()
        self.sidebar_list.get_style_context().add_class("sidebar-list")
        self.sidebar_list.connect("row-selected", self.on_sidebar_row_selected)

        self.nav_items = [
            ("dashboard", "drive-harddisk-symbolic", "nav_dashboard"),
            ("safety", "security-high-symbolic", "nav_safety"),
            ("hardware", "preferences-system-symbolic", "nav_hardware"),
            ("remote", "network-workgroup-symbolic", "nav_remote"),
            ("guides", "input-keyboard-symbolic", "nav_guides"),
            ("diagnostics", "utilities-terminal-symbolic", "nav_diagnostics"),
            ("settings", "emblem-system-symbolic", "nav_settings")
        ]

        self.nav_labels = {}
        for page_id, icon_name, tr_key in self.nav_items:
            row = Gtk.ListBoxRow()
            row.page_id = page_id
            box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            box.get_style_context().add_class("sidebar-row")
            icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
            lbl = Gtk.Label(label=self.tr(tr_key))
            lbl.set_xalign(0)
            box.pack_start(icon, False, False, 0)
            box.pack_start(lbl, True, True, 0)
            row.add(box)
            self.sidebar_list.add(row)
            self.nav_labels[page_id] = lbl

        sidebar_container.pack_start(self.sidebar_list, True, True, 0)
        main_h_box.pack_start(sidebar_container, False, False, 0)

        # ==========================================
        # RIGHT CONTENT PANEL (STACK + BOTTOM BAR)
        # ==========================================
        right_panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        main_h_box.pack_start(right_panel, True, True, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_transition_duration(150)
        right_panel.pack_start(self.stack, True, True, 0)

        # Instantiate UI Pages
        self.page_dashboard = DashboardPage(self)
        self.page_safety = SafetyPage(self)
        self.page_hardware = HardwarePage(self)
        self.page_remote = RemotePage(self)
        self.page_guides = GuidesPage(self)
        self.page_diagnostics = DiagnosticsPage(self)
        self.page_settings = SettingsPage(self)

        # Bind page widget shortcuts
        self.disk_combo = self.page_dashboard.disk_combo
        self.part_box = self.page_dashboard.part_box
        self.dep_card = self.page_dashboard.dep_card
        self.dep_msg_label = self.page_dashboard.dep_msg_label

        self.safety_card = self.page_safety.safety_card
        self.safety_status_label = self.page_safety.safety_status_label
        self.unmount_btn_box = self.page_safety.unmount_btn_box
        self.unmount_btn = self.page_safety.unmount_btn
        self.unmount_btn_lbl = self.page_safety.unmount_btn_lbl
        self.fix_ntfs_btn = self.page_safety.fix_ntfs_btn
        self.fix_ntfs_btn_lbl = self.page_safety.fix_ntfs_btn_lbl
        self.enable_fast_btn = self.page_safety.enable_fast_btn
        self.enable_fast_btn_lbl = self.page_safety.enable_fast_btn_lbl

        self.ram_scale = self.page_hardware.ram_scale
        self.cpu_scale = self.page_hardware.cpu_scale
        self.display_combo = self.page_hardware.display_combo
        self.fullscreen_chk = self.page_hardware.fullscreen_chk

        self.log_text_view = self.page_diagnostics.log_text_view
        self.log_buffer = self.page_diagnostics.log_buffer

        self.stack.add_named(self.page_dashboard, "dashboard")
        self.stack.add_named(self.page_safety, "safety")
        self.stack.add_named(self.page_hardware, "hardware")
        self.stack.add_named(self.page_remote, "remote")
        self.stack.add_named(self.page_guides, "guides")
        self.stack.add_named(self.page_diagnostics, "diagnostics")
        self.stack.add_named(self.page_settings, "settings")

        # Select first row in sidebar
        first_row = self.sidebar_list.get_row_at_index(0)
        if first_row:
            self.sidebar_list.select_row(first_row)

        # ==========================================
        # BOTTOM ACTION LAUNCHER BAR (PINNED ALWAYS)
        # ==========================================
        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        bottom_bar.get_style_context().add_class("bottom-bar")

        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_show_text(False)
        bottom_bar.pack_start(self.progress_bar, False, False, 0)


        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        
        self.start_btn, self.start_btn_lbl = make_icon_button("media-playback-start-symbolic", self.tr("start_btn"), style_class="btn-primary")
        self.start_btn.connect("clicked", self.on_start_vm_clicked)
        controls_box.pack_start(self.start_btn, True, True, 0)

        self.stop_btn, self.stop_btn_lbl = make_icon_button("media-playback-stop-symbolic", self.tr("stop_btn"), style_class="btn-danger")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self.on_stop_vm_clicked)
        controls_box.pack_start(self.stop_btn, False, False, 0)

        bottom_bar.pack_start(controls_box, False, False, 0)
        right_panel.pack_start(bottom_bar, False, False, 0)

    def on_sidebar_row_selected(self, listbox, row):
        if row and hasattr(row, "page_id"):
            self.stack.set_visible_child_name(row.page_id)

    def on_theme_changed(self, combo):
        new_theme = combo.get_active_id()
        if new_theme and new_theme != self.current_theme:
            self.current_theme = new_theme
            self.config["theme"] = new_theme
            save_config(self.config)
            self.load_css()

    def on_language_changed(self, combo):
        new_lang = combo.get_active_id()
        if new_lang and new_lang != self.current_lang:
            self.current_lang = new_lang
            self.config["language"] = new_lang
            save_config(self.config)

            if new_lang in ("id", "en"):
                self.apply_language()
            else:
                self.log_message(f"Translating application UI to '{new_lang}' via Google Translate API...")
                def on_done(success):
                    GLib.idle_add(self.apply_language)
                    if success:
                        self.log_message(f"Translation to '{new_lang}' completed successfully!")
                    else:
                        self.log_message(f"Translation to '{new_lang}' complete (using fallback).")
                batch_translate_language(new_lang, callback=on_done)

    def apply_language(self):
        if hasattr(self, "header"):
            self.header.props.subtitle = self.tr("app_subtitle")
        
        self.update_dependency_ui()

        if hasattr(self, "sidebar_title_lbl"):
            self.sidebar_title_lbl.set_text(self.tr("nav_title"))

        for page_id, icon_name, tr_key in getattr(self, "nav_items", []):
            if page_id in self.nav_labels:
                self.nav_labels[page_id].set_text(self.tr(tr_key))

        self.page_dashboard.apply_language()
        self.page_safety.apply_language()
        self.page_hardware.apply_language()
        if hasattr(self, "page_remote"):
            self.page_remote.apply_language()
        self.page_guides.apply_language()
        self.page_diagnostics.apply_language()
        self.page_settings.apply_language()

        if hasattr(self, "start_btn_lbl"): self.start_btn_lbl.set_text(self.tr("start_btn"))
        if hasattr(self, "stop_btn_lbl"): self.stop_btn_lbl.set_text(self.tr("stop_btn"))

        self.refresh_disks()


    def update_dependency_ui(self):
        missing = self.deps.get("missing_packages", [])
        if missing:
            cmd_escaped = self.deps.get('install_command', '').replace('&', '&amp;')
            msg = self.tr("dep_msg", missing=', '.join(missing), cmd=cmd_escaped)
            self.dep_msg_label.set_markup(msg)
            self.dep_card.show_all()
        else:
            self.dep_card.hide()

    def copy_install_command(self, widget):
        cmd = self.deps.get('install_command', '')
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard.set_text(cmd, -1)
        self.log_message(f"Copied install command to clipboard: {cmd}")

    def refresh_disks(self):
        self.log_message("Scanning system dependencies and physical disks...")
        self.deps = SafetyChecker.check_system_dependencies()
        self.update_dependency_ui()

        self.disks = DiskManager.get_physical_disks()
        self.disk_combo.remove_all()

        windows_index = -1
        win_suffix = self.tr("win_installed")
        for idx, disk in enumerate(self.disks):
            label = f"{disk['path']} — {disk['model']} ({disk['size_str']})"
            if disk.get("has_windows"):
                label += win_suffix
                if windows_index == -1:
                    windows_index = idx
            self.disk_combo.append_text(label)

        if len(self.disks) > 0:
            active_idx = windows_index if windows_index != -1 else 0
            self.disk_combo.set_active(active_idx)
        else:
            self.log_message("Warning: No physical storage disks found.")

    def on_disk_selected(self, combo):
        idx = combo.get_active()
        if idx < 0 or idx >= len(self.disks):
            self.selected_disk = None
            return

        self.selected_disk = self.disks[idx]
        self.update_disk_details()

    def update_disk_details(self):
        if not self.selected_disk:
            return

        for child in self.part_box.get_children():
            self.part_box.remove(child)

        parts_header = Gtk.Label(label=f"<b>Partition Layout for {self.selected_disk['path']}:</b>")
        parts_header.set_use_markup(True)
        parts_header.set_xalign(0)
        self.part_box.pack_start(parts_header, False, False, 4)

        for p in self.selected_disk.get("partitions", []):
            p_text = f"  • <b>{p['path']}</b> ({p['fstype'].upper() if p['fstype'] else 'Raw'}, {p['size_str']})"
            if p.get("label"):
                p_text += f" Label: <i>'{p['label']}'</i>"
            if p.get("is_mounted"):
                p_text += f" <span foreground='#ef5350'>[MOUNTED: {p['mountpoint']}]</span>"

            p_lbl = Gtk.Label()
            p_lbl.set_markup(p_text)
            p_lbl.set_xalign(0)
            self.part_box.pack_start(p_lbl, False, False, 1)

        self.part_box.show_all()

        safety = SafetyChecker.check_disk_safety(self.selected_disk)
        self.eval_safety_ui(safety)

    def eval_safety_ui(self, safety):
        msg_lines = []
        is_safe = safety["is_safe"]

        if safety["unmount_required"]:
            hdr = self.tr("mount_active_hdr")
            body = self.tr("mount_active_msg")
            msg_lines.append(f"<span foreground='#ef5350'><b>{hdr}</b></span> {body}")
            set_button_state(
                self.unmount_btn,
                self.unmount_btn_lbl,
                "drive-removable-media-symbolic",
                self.tr("unmount_btn"),
                state_mode="warning"
            )
            self.unmount_btn_box.show_all()
        else:
            hdr = self.tr("mount_safe_hdr")
            body = self.tr("mount_safe_msg")
            msg_lines.append(f"<span foreground='#73c991'><b>{hdr}</b></span> {body}")
            set_button_state(
                self.unmount_btn,
                self.unmount_btn_lbl,
                "emblem-ok-symbolic",
                self.tr("unmount_btn_done"),
                state_mode="used"
            )
            self.unmount_btn_box.show_all()

        if safety["is_host_disk"]:
            hdr = self.tr("dualboot_iso_hdr")
            body = self.tr("dualboot_iso_msg")
            msg_lines.append(f"<span foreground='#64b5f6'><b>{hdr}</b></span> {body}")

        self.safety_status_label.set_markup("\n".join(msg_lines))
        self.update_safety_button_styles()

        can_start = is_safe and self.deps.get("qemu_installed") and not self.launcher.is_running
        self.start_btn.set_sensitive(can_start)

    def on_unmount_clicked(self, widget):
        if not self.selected_disk:
            return

        mounted = self.selected_disk.get("mounted_partitions", [])
        for p in mounted:
            if p["mountpoint"] in ["/", "/boot", "/home"]:
                continue
            
            self.log_message(f"Unmounting partition {p['path']}...")
            success, msg = SafetyChecker.safe_unmount_partition(p["path"])
            self.log_message(msg)

        GLib.timeout_add(1000, self.refresh_disks)

    def on_fix_ntfs_clicked(self, widget):
        if not self.selected_disk:
            return

        ntfs_parts = [p for p in self.selected_disk.get("partitions", []) if p.get("fstype") == "ntfs"]
        if not ntfs_parts:
            self.log_message("Tidak ditemukan partisi NTFS pada disk yang dipilih.")
            return

        for p in ntfs_parts:
            self.log_message(f"Fixing NTFS dirty flag for partition {p['path']}...")
            success, msg = SafetyChecker.fix_ntfs_dirty_flag(p["path"])
            self.log_message(msg)
            if success:
                self.config["ntfs_reset_done"] = True
                self.config["fast_startup_active"] = False
                save_config(self.config)
                self.update_safety_button_styles()

    def on_enable_fast_startup_clicked(self, widget):
        if not self.selected_disk:
            return

        ntfs_parts = [p for p in self.selected_disk.get("partitions", []) if p.get("fstype") == "ntfs"]
        if not ntfs_parts:
            self.log_message("Tidak ditemukan partisi NTFS pada disk yang dipilih.")
            return

        for p in ntfs_parts:
            self.log_message(f"Mematikan Fast Startup & mengembalikan ke settingan default/aman untuk partisi {p['path']}...")
            success, msg = SafetyChecker.disable_fast_startup(p["path"])
            self.log_message(msg)
            if success:
                self.config["fast_startup_active"] = False
                self.config["ntfs_reset_done"] = True
                save_config(self.config)
                self.update_safety_button_styles()

    def update_safety_button_styles(self):
        if not hasattr(self, "fix_ntfs_btn") or not hasattr(self, "enable_fast_btn"):
            return

        fast_startup_active = self.config.get("fast_startup_active", False)
        ntfs_reset_done = self.config.get("ntfs_reset_done", False)

        if ntfs_reset_done:
            set_button_state(
                self.fix_ntfs_btn,
                self.fix_ntfs_btn_lbl,
                "emblem-ok-symbolic",
                self.tr("fix_ntfs_btn_done"),
                state_mode="used"
            )
            set_button_state(
                self.enable_fast_btn,
                self.enable_fast_btn_lbl,
                "system-run-symbolic",
                self.tr("enable_fast_btn"),
                state_mode="warning"
            )
        elif fast_startup_active:
            set_button_state(
                self.enable_fast_btn,
                self.enable_fast_btn_lbl,
                "emblem-ok-symbolic",
                self.tr("enable_fast_btn_done"),
                state_mode="used"
            )
            set_button_state(
                self.fix_ntfs_btn,
                self.fix_ntfs_btn_lbl,
                "system-run-symbolic",
                self.tr("fix_ntfs_btn"),
                state_mode="warning"
            )
        else:
            set_button_state(
                self.fix_ntfs_btn,
                self.fix_ntfs_btn_lbl,
                "system-run-symbolic",
                self.tr("fix_ntfs_btn"),
                state_mode="warning"
            )
            set_button_state(
                self.enable_fast_btn,
                self.enable_fast_btn_lbl,
                "system-run-symbolic",
                self.tr("enable_fast_btn"),
                state_mode="warning"
            )

    def on_key_press_event(self, widget, event):
        """Global keypress handler for application shortcuts (Ctrl + Alt + H)."""
        state = event.state & Gdk.ModifierType.MODIFIER_MASK
        ctrl_alt = (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK)
        if (state & ctrl_alt) == ctrl_alt and event.keyval in (Gdk.KEY_h, Gdk.KEY_H):
            self._show_launch_guide_dialog(is_manual=True)
            return True
        return False

    def _show_launch_guide_dialog(self, is_manual=False):
        """Shows emulator-style quick controls & shortcuts dialog (clean symbolic styling without emoticons)."""
        dialog = Gtk.Dialog(
            title=self.tr("guide_dialog_title"),
            transient_for=self,
            flags=0
        )
        dialog.set_modal(True)
        dialog.set_keep_above(True)
        dialog.set_default_size(500, -1)

        box = dialog.get_content_area()
        box.set_spacing(12)
        box.set_margin_top(16)
        box.set_margin_bottom(16)
        box.set_margin_start(16)
        box.set_margin_end(16)

        hdr_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        icon = Gtk.Image.new_from_icon_name("help-about-symbolic", Gtk.IconSize.DND)
        lbl_hdr = Gtk.Label()
        lbl_hdr.set_markup(f"<b><big>{self.tr('guide_dialog_title')}</big></b>")
        hdr_box.pack_start(icon, False, False, 0)
        hdr_box.pack_start(lbl_hdr, False, False, 0)
        box.pack_start(hdr_box, False, False, 0)

        sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        box.pack_start(sep, False, False, 0)

        body_lbl = Gtk.Label()
        body_lbl.set_xalign(0)
        body_lbl.set_line_wrap(True)
        body_lbl.set_markup(self.tr("guide_dialog_markup"))
        box.pack_start(body_lbl, False, False, 0)

        dont_show_chk = None
        if not is_manual:
            dont_show_chk = Gtk.CheckButton(label=self.tr("dont_show_again"))
            dont_show_chk.set_active(False)
            box.pack_start(dont_show_chk, False, False, 4)

        if is_manual:
            dialog.add_button("Tutup", Gtk.ResponseType.OK)
        else:
            dialog.add_button(self.tr("btn_cancel"), Gtk.ResponseType.CANCEL)
            btn_continue = dialog.add_button(self.tr("btn_continue"), Gtk.ResponseType.OK)
            btn_continue.get_style_context().add_class("suggested-action")

        box.show_all()
        response = dialog.run()

        if dont_show_chk:
            dont_show = dont_show_chk.get_active()
            if dont_show:
                self.config["show_launch_guide"] = False
                save_config(self.config)

        dialog.destroy()
        return response == Gtk.ResponseType.OK

    def on_start_vm_clicked(self, widget):
        if not self.selected_disk:
            return

        if self.config.get("show_launch_guide", True):
            if not self._show_launch_guide_dialog():
                self.log_message("VM boot cancelled by user from shortcut guide dialog.")
                return

        ram_mb = int(self.ram_scale.get_value())
        cpu_cores = int(self.cpu_scale.get_value())
        display = self.display_combo.get_active_id() or "gtk"
        fullscreen = self.fullscreen_chk.get_active()

        self.log_message(f"Initiating VM boot for physical disk {self.selected_disk['path']} (Fullscreen={fullscreen})...")
        success = self.launcher.start_vm(
            disk_path=self.selected_disk["path"],
            ram_mb=ram_mb,
            cpu_cores=cpu_cores,
            display_type=display,
            fullscreen=fullscreen
        )

        if success:
            self.start_btn.set_sensitive(False)
            self.stop_btn.set_sensitive(True)
            self.progress_bar.set_fraction(0.5)

    def on_stop_vm_clicked(self, widget):
        self.launcher.stop_vm()

    def on_vm_status_changed(self, status):
        def update_ui():
            if status == "RUNNING":
                self.start_btn.set_sensitive(False)
                self.stop_btn.set_sensitive(True)
                self.progress_bar.set_fraction(1.0)
            else:
                self.start_btn.set_sensitive(True)
                self.stop_btn.set_sensitive(False)
                self.progress_bar.set_fraction(0.0)
        GLib.idle_add(update_ui)


    def on_connect_remote_clicked(self, widget):
        if not hasattr(self, "page_remote") or not hasattr(self, "remote_launcher"):
            return

        proto = self.page_remote.proto_combo.get_active_id() or "rdp"
        host = self.page_remote.host_entry.get_text().strip() or "127.0.0.1"
        try:
            port = int(self.page_remote.port_entry.get_text().strip())
        except ValueError:
            port = 3389 if proto == "rdp" else 5900

        user = self.page_remote.user_entry.get_text().strip()
        pwd = self.page_remote.pass_entry.get_text().strip()
        fullscreen = self.page_remote.fullscreen_chk.get_active()
        clip = self.page_remote.clip_chk.get_active()
        sound = self.page_remote.sound_chk.get_active()
        dynres = self.page_remote.dynres_chk.get_active()

        add_remote_history({
            "host": host,
            "port": port,
            "proto": proto,
            "user": user
        })
        self.page_remote.refresh_history()

        self.remote_launcher.start_remote_session(
            protocol=proto,
            host=host,
            port=port,
            username=user,
            password=pwd,
            fullscreen=fullscreen,
            clipboard=clip,
            sound=sound,
            dynamic_res=dynres
        )

    def on_disconnect_remote_clicked(self, widget):
        if hasattr(self, "remote_launcher"):
            self.remote_launcher.stop_remote_session()

    def on_remote_status_changed(self, status):
        def update_ui():
            if hasattr(self, "page_remote"):
                if status == "RUNNING":
                    self.page_remote.connect_btn.set_sensitive(False)
                    self.page_remote.disconnect_btn.set_sensitive(True)
                else:
                    self.page_remote.connect_btn.set_sensitive(True)
                    self.page_remote.disconnect_btn.set_sensitive(False)
        GLib.idle_add(update_ui)

    def log_message(self, message):
        def append_log():
            end_iter = self.log_buffer.get_end_iter()
            self.log_buffer.insert(end_iter, f"{message}\n")
            mark = self.log_buffer.create_mark(None, self.log_buffer.get_end_iter(), False)
            self.log_text_view.scroll_to_mark(mark, 0.0, True, 0.0, 1.0)
        GLib.idle_add(append_log)
