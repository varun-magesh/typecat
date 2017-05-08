import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

class GtkFileChooser(Gtk.Box):

    def __new__(cls, *args, **kwargs):
        builder = Gtk.Builder()
        builder.add_from_file("xml/filechooser.glade")
        self = builder.get_object("box1")
        self.__class__ = cls
        return self

    def __init__(self, title, defaultPath):

        self.pathbox.set_text(defaultPath)
        self.pathdesc.set_text(title)
        self.button.connect("clicked", self.openBrowser)

    def openBrowser(button):
        dialog = Gtk.FileChooserDialog("Choose a directory", Gtk.Dialog(),
                                       Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                        "Select", Gtk.ResponseType.OK))
        resp = dialog.run()
        if resp == Gtk.ResponseType.OK:
            pathbox.set_text(dialog.get_filename())
        dialog.destroy()

win = Gtk.Window()

box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL,spacing=6)
box.pack_start(GtkFileChooser("Cache Location", os.path.dirname(os.path.realpath(__file__))), True, True, 0)
box.pack_end(GtkFileChooser("help", "woohoo"), True, True, 0)
win.add(box)
win.show_all()
Gtk.main()