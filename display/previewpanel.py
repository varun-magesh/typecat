import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class PreviewPanel(Gtk.Box):

    def __init__(self, refresh):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.set_border_width(5)
        self.preview = Gtk.Entry()
        self.preview.set_text("Handgloves")
        self.refresh = refresh
        self.preview.connect("activate", self.refresh)
        self.pack_start(self.preview, True, True, 5)
        self.preview_size = Gtk.SpinButton()
        self.preview_size.set_halign(Gtk.Align.END)
        self.preview_size.set_value(75)
        self.pack_start(self.preview_size, False, False, 5)

    # def on_change_preview_size(spinner):
    #
    # def on_change_preview_text(entry):

