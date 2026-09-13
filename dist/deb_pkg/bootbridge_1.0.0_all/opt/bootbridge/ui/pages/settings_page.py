import multiprocessing
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from core.translator import SUPPORTED_LANGUAGES
from ui.components import make_card_header

class SettingsPage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page_sett_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_sett_box.set_margin_top(16)
        page_sett_box.set_margin_bottom(16)
        page_sett_box.set_margin_start(16)
        page_sett_box.set_margin_end(16)
        self.add(page_sett_box)

        # Settings Card 1: Appearance & Language
        sett_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        sett_card.get_style_context().add_class("card")

        sett_title_box, self.sett_title_lbl = make_card_header("emblem-system-symbolic", app.tr("settings_card_title"))
        sett_card.pack_start(sett_title_box, False, False, 0)

        sett_grid = Gtk.Grid()
        sett_grid.set_column_spacing(16)
        sett_grid.set_row_spacing(14)

        # Theme Selector
        self.sett_theme_lbl = Gtk.Label(label=app.tr("theme_setting"))
        self.sett_theme_lbl.set_xalign(0)
        sett_grid.attach(self.sett_theme_lbl, 0, 0, 1, 1)

        self.sett_theme_combo = Gtk.ComboBoxText()
        self.sett_theme_combo.append("dark", app.tr("theme_dark"))
        self.sett_theme_combo.append("light", app.tr("theme_light"))
        self.sett_theme_combo.set_active_id(app.current_theme)
        self.sett_theme_combo.connect("changed", app.on_theme_changed)
        sett_grid.attach(self.sett_theme_combo, 1, 0, 1, 1)

        # Language Selector (Google Translate API)
        self.sett_lang_lbl = Gtk.Label(label=app.tr("lang_setting"))
        self.sett_lang_lbl.set_xalign(0)
        sett_grid.attach(self.sett_lang_lbl, 0, 1, 1, 1)

        self.sett_lang_combo = Gtk.ComboBoxText()
        for code, label in SUPPORTED_LANGUAGES:
            self.sett_lang_combo.append(code, label)
        self.sett_lang_combo.set_active_id(app.current_lang)
        self.sett_lang_combo.connect("changed", app.on_language_changed)
        sett_grid.attach(self.sett_lang_combo, 1, 1, 1, 1)

        sett_card.pack_start(sett_grid, False, False, 0)
        page_sett_box.pack_start(sett_card, False, False, 0)

        # Settings Card 2: System Hypervisor Specs
        sys_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        sys_card.get_style_context().add_class("card")

        sys_title_box, self.sys_title_lbl = make_card_header("computer-symbolic", app.tr("sys_info_title"))
        sys_card.pack_start(sys_title_box, False, False, 0)

        try:
            with open("/proc/meminfo", "r") as f:
                total_kb = int([line.split()[1] for line in f if "MemTotal" in line][0])
            total_ram_mb = total_kb // 1024
        except Exception:
            total_ram_mb = 8192

        self.sys_info_lbl = Gtk.Label()
        self.sys_info_lbl.set_xalign(0)
        self.sys_info_lbl.set_markup(
            f"• <b>Host Cores:</b> {multiprocessing.cpu_count()} CPU Threads\n"
            f"• <b>Memory RAM:</b> {int(total_ram_mb/1024)} GB Total\n"
            f"• <b>KVM Acceleration:</b> {'Supported &amp; Enabled' if app.deps.get('kvm_available') else 'Disabled / Unavailable'}\n"
            f"• <b>QEMU Package:</b> {'Installed' if app.deps.get('qemu_installed') else 'Missing'}\n"
            f"• <b>OVMF Firmware:</b> {'Installed' if app.deps.get('ovmf_installed') else 'Missing'}"
        )
        sys_card.pack_start(self.sys_info_lbl, False, False, 0)
        page_sett_box.pack_start(sys_card, False, False, 0)

    def apply_language(self):
        self.sett_title_lbl.set_text(self.app.tr("settings_card_title"))
        self.sett_theme_lbl.set_text(self.app.tr("theme_setting"))
        self.sett_lang_lbl.set_text(self.app.tr("lang_setting"))
        self.sys_title_lbl.set_text(self.app.tr("sys_info_title"))

        self.sett_theme_combo.remove_all()
        self.sett_theme_combo.append("dark", self.app.tr("theme_dark"))
        self.sett_theme_combo.append("light", self.app.tr("theme_light"))
        self.sett_theme_combo.set_active_id(self.app.current_theme)

        self.sett_lang_combo.handler_block_by_func(self.app.on_language_changed)
        self.sett_lang_combo.set_active_id(self.app.current_lang)
        self.sett_lang_combo.handler_unblock_by_func(self.app.on_language_changed)
