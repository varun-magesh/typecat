from typecat.font import Font
from typecat.display.fontbox import FontBox
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class FontBoxBox(Gtk.ScrolledWindow):
    def __init__(self):
        Gtk.ScrolledWindow.__init__(self)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_border_width(10)
        self.set_hexpand(True)
        self.set_vexpand(True)

        self.flowbox = Gtk.FlowBox()
        self.flowbox.set_valign(Gtk.Align.START)
        self.flowbox.set_max_children_per_line(30)
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flowbox.set_homogeneous(True)

        self.entry= Gtk.Entry()
        # FIXME URGENT this method is deprecated we should use CSS instead

        self.preview_text = "Handgloves"

        self.add(self.flowbox)

        self.refresh()

    def refresh(self):
        for i in self.flowbox.get_children():
            i.destroy()
        for num, name in enumerate(Font.fonts.keys()):
            b = FontBox(Font.fonts[name])
            self.flowbox.add(b)
        self.flowbox.show_all()

    def text(self, box, child, *user_args):
        child.set_text(self.preview_text)

    def set_text(self, text):
        self.preview_text = text
        self.flowbox.set_selection_mode(Gtk.SelectionMode.MULTIPLE)
        self.flowbox.select_all()
        self.flowbox.selected_foreach(self.text)
        self.show_all()
        self.flowbox.unselect_all()
        self.flowbox.set_selection_mode(Gtk.SelectionMode.NONE)

    def set_sort_func(self, func):
        self.flowbox.set_sort_func(func)
