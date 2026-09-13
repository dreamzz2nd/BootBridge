import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.components import make_icon_card_title

class DiagnosticsPage(Gtk.Box):
    def __init__(self, app):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.app = app
        self.set_margin_top(16)
        self.set_margin_bottom(16)
        self.set_margin_start(16)
        self.set_margin_end(16)

        log_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        log_card.get_style_context().add_class("card")

        log_header, self.log_title_lbl = make_icon_card_title("utilities-terminal-symbolic", app.tr("log_title"))
        log_card.pack_start(log_header, False, False, 0)

        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(350)
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)

        self.log_text_view = Gtk.TextView()
        self.log_text_view.set_editable(False)
        self.log_text_view.get_style_context().add_class("log-view")
        self.log_buffer = self.log_text_view.get_buffer()

        scrolled.add(self.log_text_view)
        log_card.pack_start(scrolled, True, True, 0)
        self.pack_start(log_card, True, True, 0)

    def apply_language(self):
        self.log_title_lbl.set_text(self.app.tr("log_title"))
