import manager
from display.fontbox import FontBox
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class FontBoxBox(Gtk.Box):
    def __init__(self):
        Gtk.Box.__init__(self)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(10)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

        scroll.add(self.flowbox)
        self.pack_start(scroll, True, True, 0)
        self.show_all()

    def refresh(self):
        for i in self.flowbox.get_children():
            i.destroy(self)
        for num, name in enumerate(manager.keys):
            b = FontBox(manager[name])
            self.flowbox.add(b)
        self.flowbox.show_all()
