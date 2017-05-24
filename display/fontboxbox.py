import manager
from display.fontbox import FontBox
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class FontBoxBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(30)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        self.add(self.flowbox)

        self.refresh()

    def refresh(self):
        for i in self.flowbox.get_children():
            i.destroy()
        for num, name in enumerate(manager.keys):
            b = FontBox(manager.fonts[name])
            self.flowbox.add(b)
        self.flowbox.show_all()
