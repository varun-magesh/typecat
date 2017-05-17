import font2img as f2i
import manager
from font import Font
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Pango

class FontInfo(Gtk.Window):

    def __init__(self, font, text="Handgloves", size=(100, 350), font_size=75):
        Gtk.Window.__init__(self, title="TextView Example")

        self.font = font
        self.font_size = 75
        self.font.set_size(self.font_size)
        self.text = text
        self.size = size

        self.set_default_size(100, 350)

        self.grid = Gtk.Grid()
        self.add(self.grid)

        self.image = Gtk.Image()
        self.image.set_from_pixbuf(f2i.multiline_gtk(self.text, self.font.pilfont, self.size))
        self.pack_start (self.image, False, False, 0)


f = Font("/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf")
print(str(f))
win = FontInfo(f)
win.connect("delete-event", Gtk.main_quit)
win.show_all()
Gtk.main()
