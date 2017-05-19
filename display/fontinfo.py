import font2img as f2i
import manager
from font import Font
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class FontInfo(Gtk.Box):

    def __init__(self, font, text="Handgloves", size=(300, 200), font_size=75):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL)

        self.font = font
        self.font_size = 35
        self.font.set_size(self.font_size)
        self.text = text

        self.size = size

        self.title = Gtk.Label(halign=Gtk.Align.START)
        self.title.set_markup("<b>{}</b>".format(self.font.name))
        self.pack_start(self.title, False, False, 0)

        self.image = Gtk.Image()
        self.image.set_from_pixbuf(f2i.multiline_gtk(self.text, self.font.pilfont, self.size))
        self.pack_start(self.image, False, False, 0)

