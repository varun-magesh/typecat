import manager
from display.fontbox import FontBox
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class FontBoxBox(Gtk.FlowBox):
    def __init__(self):
        Gtk.FlowBox.__init__(self)
        self.set_valign(Gtk.Align.START)
        self.set_max_children_per_line(30)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

    def refresh(self):
        for i in self.get_children():
            i.destroy()
        for num, name in enumerate(manager.keys):
            b = FontBox(manager.fonts[name])
            self.add(b)
        self.add(FontBox(manager.fonts[manager.keys[20]]))
        self.show_all()
