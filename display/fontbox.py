import font2img as f2i
import manager
from font import Font
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class FontBox(Gtk.FlowBoxChild):

    def __init__(self, font, text="Handgloves", size=(200, 150), font_size=75):
        Gtk.FlowBoxChild.__init__(self)
        self.box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_border_width(5)
        self.font = font
        self.font_size = int(size[0]/9)
        self.font.set_size(self.font_size)
        self.text = text

        self.size = size

        self.title = Gtk.Label(halign=Gtk.Align.START)
        self.title.set_markup("<b>{}</b>".format(self.font.name))
        self.box.pack_start(self.title, False, False, 0)

        self.image = Gtk.Image(halign=Gtk.Align.START)
        self.image.set_from_pixbuf(f2i.multiline_gtk(self.text, self.font.pilfont, self.size))
        self.box.pack_start(self.image, False, False, 0)
        
        self.add(self.box)

