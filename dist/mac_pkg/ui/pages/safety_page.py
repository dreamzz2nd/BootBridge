import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.components import make_card_header, make_icon_button

class SafetyPage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.box.set_margin_top(16)
        self.box.set_margin_bottom(16)
        self.box.set_margin_start(16)
        self.box.set_margin_end(16)
        self.add(self.box)

        self.safety_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.safety_card.get_style_context().add_class("card")

        safety_title_box, self.safety_title_lbl = make_card_header("security-high-symbolic", app.tr("safety_card_title"))
        self.safety_card.pack_start(safety_title_box, False, False, 0)

        self.safety_status_label = Gtk.Label(label="Checking safety...")
        self.safety_status_label.set_xalign(0)
        self.safety_status_label.set_line_wrap(True)
        self.safety_card.pack_start(self.safety_status_label, False, False, 0)

        self.unmount_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.unmount_btn, self.unmount_btn_lbl = make_icon_button("drive-removable-media-symbolic", app.tr("unmount_btn"), style_class="btn-warning")
        self.unmount_btn.connect("clicked", app.on_unmount_clicked)
        self.unmount_btn_box.pack_start(self.unmount_btn, False, False, 0)

        self.fix_ntfs_btn, self.fix_ntfs_btn_lbl = make_icon_button("system-run-symbolic", app.tr("fix_ntfs_btn"), style_class="btn-warning")
        self.fix_ntfs_btn.connect("clicked", app.on_fix_ntfs_clicked)
        self.unmount_btn_box.pack_start(self.fix_ntfs_btn, False, False, 0)

        self.enable_fast_btn, self.enable_fast_btn_lbl = make_icon_button("system-run-symbolic", app.tr("enable_fast_btn"), style_class="btn-warning")
        self.enable_fast_btn.connect("clicked", app.on_enable_fast_startup_clicked)
        self.unmount_btn_box.pack_start(self.enable_fast_btn, False, False, 0)

        self.safety_card.pack_start(self.unmount_btn_box, False, False, 0)
        self.box.pack_start(self.safety_card, False, False, 0)

    def apply_language(self):
        self.safety_title_lbl.set_text(self.app.tr("safety_card_title"))
        if hasattr(self.app, "update_safety_button_styles"):
            self.app.update_safety_button_styles()
