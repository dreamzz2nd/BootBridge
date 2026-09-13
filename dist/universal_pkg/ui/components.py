"""
Reusable GTK UI Component Helpers for BootBridge
"""

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

def make_card_header(icon_name, title_text):
    """Creates a card header box with a GTK symbolic icon and title label."""
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=title_text)
    label.set_xalign(0)
    label.get_style_context().add_class("card-title")
    box.pack_start(icon, False, False, 0)
    box.pack_start(label, False, False, 0)
    return box, label

def make_icon_button(icon_name, label_text, style_class=None):
    """Creates a GTK Button containing a GTK symbolic icon and label."""
    btn = Gtk.Button()
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    box.set_halign(Gtk.Align.CENTER)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=label_text)
    box.pack_start(icon, False, False, 0)
    box.pack_start(label, False, False, 0)
    btn.add(box)
    if style_class:
        btn.get_style_context().add_class(style_class)
    return btn, label

def make_icon_card_title(icon_name, title_text):
    """Creates a card header box with a symbolic icon header."""
    header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
    icon = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
    label = Gtk.Label(label=title_text)
    label.get_style_context().add_class("card-title")
    header_box.pack_start(icon, False, False, 0)
    header_box.pack_start(label, False, False, 0)
    return header_box, label

def set_button_state(btn, label_widget, icon_name, text, state_mode):
    """
    Updates GTK button label, icon, and CSS class based on state_mode:
    - 'used': Gray button (action active / already applied)
    - 'warning': Orange button (action ready to be executed)
    - 'danger': Red button (emergency / stop action)
    """
    if not btn or not label_widget:
        return
    label_widget.set_text(text)
    ctx = btn.get_style_context()
    
    ctx.remove_class("btn-warning")
    ctx.remove_class("btn-success")
    ctx.remove_class("btn-danger")
    ctx.remove_class("btn-used")

    if state_mode == "used":
        ctx.add_class("btn-used")
    elif state_mode == "danger":
        ctx.add_class("btn-danger")
    else:
        ctx.add_class("btn-warning")

    child = btn.get_child()
    if isinstance(child, Gtk.Box):
        for box_child in child.get_children():
            if isinstance(box_child, Gtk.Image):
                box_child.set_from_icon_name(icon_name, Gtk.IconSize.BUTTON)
                break
