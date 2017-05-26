import font2img as f2i
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class FontBox(Gtk.FlowBoxChild):

    def set_text(self, arg1):
        if arg1 is str:
            self.text = arg1
        elif arg1 is int:
            self.size = arg1
        self.box = Gtk.Box()
        self.box.set_border_width(5)
        try:
            self.box.remove(self.image)
        except AttributeError:
            pass
        self.image = Gtk.Image(halign=Gtk.Align.CENTER)
        self.image.set_from_pixbuf(f2i.multiline_gtk(self.text, self.font.pilfont, self.size))
        self.box.pack_start(self.image, True, False, 0)
        self.frame.add(self.box)

    def __init__(self, font, text="Handgloves", size=(200, 150), font_size=75):
        Gtk.FlowBoxChild.__init__(self)
        self.frame = Gtk.Frame()
        self.set_border_width(5)
        self.font = font
        self.font_size = int(size[0]/9)
        self.font.set_size(self.font_size)
        self.text = text

        self.size = size

        self.title = self.font.name if len(self.font.name) < 30 else self.font.name[:27] + "..."
        self.frame.set_label(self.title)
        self.frame.set_label_align(.1, .5)
        self.set_text(text)

        self.add(self.frame)

