import multiprocessing
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from ui.components import make_card_header

class HardwarePage(Gtk.ScrolledWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        page_hw_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        page_hw_box.set_margin_top(16)
        page_hw_box.set_margin_bottom(16)
        page_hw_box.set_margin_start(16)
        page_hw_box.set_margin_end(16)
        self.add(page_hw_box)

        config_card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        config_card.get_style_context().add_class("card")

        config_title_box, self.config_title_lbl = make_card_header("preferences-system-symbolic", app.tr("config_card_title"))
        config_card.pack_start(config_title_box, False, False, 0)

        grid = Gtk.Grid()
        grid.set_column_spacing(16)
        grid.set_row_spacing(14)

        try:
            with open("/proc/meminfo", "r") as f:
                total_kb = int([line.split()[1] for line in f if "MemTotal" in line][0])
            total_ram_mb = total_kb // 1024
        except Exception:
            total_ram_mb = 8192

        if total_ram_mb <= 4096:
            rec_ram_mb = 2048
        elif total_ram_mb <= 8192:
            rec_ram_mb = 3072
        elif total_ram_mb <= 16384:
            rec_ram_mb = 6144
        else:
            rec_ram_mb = 8192

        max_cores = multiprocessing.cpu_count()
        if max_cores <= 2:
            rec_cores = 1
        elif max_cores <= 4:
            rec_cores = 2
        elif max_cores <= 8:
            rec_cores = 4
        else:
            rec_cores = max_cores // 2

        self.rec_ram_mb = rec_ram_mb
        self.rec_cores = rec_cores

        self.ram_lbl = Gtk.Label(label=app.tr("ram_alloc"))
        self.ram_lbl.set_xalign(0)
        grid.attach(self.ram_lbl, 0, 0, 1, 1)

        max_slider_ram = max(rec_ram_mb, min(16384, (total_ram_mb // 1024) * 1024))
        self.ram_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1024, max_slider_ram, 1024)
        self.ram_scale.set_value(rec_ram_mb)
        self.ram_scale.set_digits(0)
        self.ram_scale.set_hexpand(True)
        self.ram_scale.set_draw_value(True)
        grid.attach(self.ram_scale, 1, 0, 1, 1)

        self.cpu_lbl = Gtk.Label(label=app.tr("cpu_cores"))
        self.cpu_lbl.set_xalign(0)
        grid.attach(self.cpu_lbl, 0, 1, 1, 1)

        self.cpu_scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 1, max_cores, 1)
        self.cpu_scale.set_value(rec_cores)
        self.cpu_scale.set_digits(0)
        self.cpu_scale.set_hexpand(True)
        self.cpu_scale.set_draw_value(True)
        grid.attach(self.cpu_scale, 1, 1, 1, 1)

        self.update_scale_marks()

        self.display_lbl = Gtk.Label(label=app.tr("display_engine"))
        self.display_lbl.set_xalign(0)
        grid.attach(self.display_lbl, 0, 2, 1, 1)

        self.display_combo = Gtk.ComboBoxText()
        self.display_combo.append("gtk", "Native GTK Window (QXL 2D/3D)")
        self.display_combo.append("sdl", "SDL Hardware Window")
        self.display_combo.append("spice", "SPICE Protocol (Remote/Local)")
        self.display_combo.set_active(0)
        grid.attach(self.display_combo, 1, 2, 1, 1)

        self.fullscreen_chk = Gtk.CheckButton(label=app.tr("fullscreen_chk"))
        grid.attach(self.fullscreen_chk, 0, 3, 2, 1)

        config_card.pack_start(grid, False, False, 0)
        page_hw_box.pack_start(config_card, False, False, 0)

    def update_scale_marks(self):
        rec_lbl = self.app.tr("recommended")
        self.ram_scale.clear_marks()
        self.ram_scale.add_mark(self.rec_ram_mb, Gtk.PositionType.BOTTOM, f"{rec_lbl} ({int(self.rec_ram_mb/1024)} GB)")
        self.ram_scale.connect("format-value", lambda scale, val: f"{int(val/1024)} GB ({int(val)} MB)" + (f" ({rec_lbl})" if int(val) == self.rec_ram_mb else ""))

        self.cpu_scale.clear_marks()
        self.cpu_scale.add_mark(self.rec_cores, Gtk.PositionType.BOTTOM, f"{rec_lbl} ({self.rec_cores} Cores)")
        self.cpu_scale.connect("format-value", lambda scale, val: f"{int(val)} Core" + ("s" if int(val) > 1 else "") + (f" ({rec_lbl})" if int(val) == self.rec_cores else ""))

    def apply_language(self):
        self.config_title_lbl.set_text(self.app.tr("config_card_title"))
        self.ram_lbl.set_text(self.app.tr("ram_alloc"))
        self.cpu_lbl.set_text(self.app.tr("cpu_cores"))
        self.display_lbl.set_text(self.app.tr("display_engine"))
        self.fullscreen_chk.set_label(self.app.tr("fullscreen_chk"))
        self.update_scale_marks()
