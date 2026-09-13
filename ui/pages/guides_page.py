import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.components import make_icon_card_title

class GuidesPage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page_guides_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_guides_box.set_margin_top(16)
        page_guides_box.set_margin_bottom(16)
        page_guides_box.set_margin_start(16)
        page_guides_box.set_margin_end(16)
        self.add(page_guides_box)

        # Shortcuts Card
        shortcut_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        shortcut_card.get_style_context().add_class("card")

        shortcut_header, self.shortcut_title_lbl = make_icon_card_title("input-keyboard-symbolic", app.tr("shortcut_title"))
        shortcut_card.pack_start(shortcut_header, False, False, 0)

        self.shortcut_text = Gtk.Label()
        self.shortcut_text.set_xalign(0)
        self.shortcut_text.set_line_wrap(True)
        self.shortcut_text.set_markup(app.tr("shortcut_markup"))
        shortcut_card.pack_start(self.shortcut_text, False, False, 0)
        page_guides_box.pack_start(shortcut_card, False, False, 0)

        # Troubleshooting Card
        help_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        help_card.get_style_context().add_class("card")

        help_header, self.help_title_lbl = make_icon_card_title("help-faq-symbolic", app.tr("help_title"))
        help_card.pack_start(help_header, False, False, 0)

        self.help_text = Gtk.Label()
        self.help_text.set_xalign(0)
        self.help_text.set_line_wrap(True)
        self.help_text.set_markup(app.tr("help_markup"))
        help_card.pack_start(self.help_text, False, False, 0)
        page_guides_box.pack_start(help_card, False, False, 0)

    def apply_language(self):
        self.shortcut_title_lbl.set_text(self.app.tr("shortcut_title"))
        self.shortcut_text.set_markup(self.app.tr("shortcut_markup"))
        self.help_title_lbl.set_text(self.app.tr("help_title"))
        self.help_text.set_markup(self.app.tr("help_markup"))
