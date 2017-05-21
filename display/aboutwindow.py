import gi
import os

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GtkAboutWindow(Gtk.AboutDialog):
    def __init__(self):
        Gtk.AboutDialog.__init__(self)
        self.set_program_name("typecat")
        self.set_authors(["Varun Iyer", "Timothy Kanarsky"])
        self.set_comments("Organize and find fonts with the magic of neural networks\nContribute:")
        self.set_website("typecat.github.io")
        self.set_website_label("typecat.github.io")

        self.set_logo_icon_name("accessories-character-map")
        self.set_license_type(Gtk.License.MIT_X11)
        self.set_license("\n".join(open("../LICENSE.txt", 'r').readlines()))
        self.set_version("0.5.0")

win = GtkAboutWindow()
win.show_all()
win.connect("delete-event", Gtk.main_quit)
Gtk.main()
