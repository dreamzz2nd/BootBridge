import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.components import make_card_header, make_icon_button

class DashboardPage(Gtk.ScrolledWindow):
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

        # Dependency Warning Card
        self.dep_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        self.dep_card.get_style_context().add_class("card")
        self.dep_card.get_style_context().add_class("badge-warning")
        
        dep_title_box, self.dep_title_lbl = make_card_header("dialog-warning-symbolic", app.tr("dep_title"))
        self.dep_card.pack_start(dep_title_box, False, False, 0)

        self.dep_msg_label = Gtk.Label()
        self.dep_msg_label.set_xalign(0)
        self.dep_msg_label.set_line_wrap(True)
        self.dep_card.pack_start(self.dep_msg_label, False, False, 0)

        dep_btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.copy_cmd_btn, self.copy_cmd_btn_lbl = make_icon_button("edit-copy-symbolic", app.tr("copy_cmd"))
        self.copy_cmd_btn.connect("clicked", app.copy_install_command)
        dep_btn_box.pack_start(self.copy_cmd_btn, False, False, 0)
        self.dep_card.pack_start(dep_btn_box, False, False, 0)
        self.box.pack_start(self.dep_card, False, False, 0)

        # Disk Card
        disk_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        disk_card.get_style_context().add_class("card")

        disk_title_box, self.disk_title_lbl = make_card_header("drive-harddisk-symbolic", app.tr("disk_card_title"))
        disk_card.pack_start(disk_title_box, False, False, 0)

        combo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        self.combo_label = Gtk.Label(label=app.tr("target_disk"))
        self.combo_label.set_xalign(0)
        combo_box.pack_start(self.combo_label, False, False, 0)

        self.disk_combo = Gtk.ComboBoxText()
        self.disk_combo.connect("changed", app.on_disk_selected)
        combo_box.pack_start(self.disk_combo, True, True, 0)
        disk_card.pack_start(combo_box, False, False, 0)

        self.part_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        disk_card.pack_start(self.part_box, False, False, 0)
        self.box.pack_start(disk_card, False, False, 0)

    def apply_language(self):
        self.dep_title_lbl.set_text(self.app.tr("dep_title"))
        self.copy_cmd_btn_lbl.set_text(self.app.tr("copy_cmd"))
        self.disk_title_lbl.set_text(self.app.tr("disk_card_title"))
        self.combo_label.set_text(self.app.tr("target_disk"))
