import config
from os.path import isdir
import manager
import threading
from os import mkdir
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GtkFileChooser(Gtk.Box):
    def __init__(self, title, default):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        if not title == "":
            self.pathdesc = Gtk.Label()
            self.pathdesc.set_markup("<b>" + title + "</b>")
            self.pathdesc.set_alignment(0, 0)
            self.pack_start(self.pathdesc, False, False, 0)

        self.entrybox = Gtk.Entry()
        self.entrybox.set_text(default)
        self.browsebutton = Gtk.Button("Browse")
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.box1.pack_start(self.entrybox, True, True, 0)
        self.box1.pack_end(self.browsebutton, False, False, 0)
        self.pack_start(self.box1, True, True, 0)
        self.browsebutton.connect("clicked", self.open_browser)

    def open_browser(self, button):
        dialog = Gtk.FileChooserDialog("Choose a directory", Gtk.Window(), Gtk.FileChooserAction.SELECT_FOLDER,
                                       (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL, "Select", Gtk.ResponseType.OK))
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            self.entrybox.set_text(dialog.get_filename())
        dialog.destroy()

    def get_file(self):
        return self.entrybox.get_text()


class RemovableGtkFileChooser(Gtk.Box):
    def __init__(self, title, default):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        self.fc = GtkFileChooser(title, default)
        self.pack_start(self.fc, True, True, 0)
        removebutt = Gtk.Button("X")
        self.pack_end(removebutt, False, False, 0)
        removebutt.connect("clicked", self.killme)

    def killme(self, button):
        self.destroy()

    def get_file(self):
        return self.fc.get_file()


class GtkConfigWindow(Gtk.Window):
    def finish(self, widget):
        config.CACHE_LOCATION = self.cache.get_file()
        config.FONT_DIRS = []
        for i in self.font_dirs:
            if i.get_file() != "":
                config.FONT_DIRS.append(i.get_file())
        if not isdir(config.CACHE_LOCATION):
            mkdir(config.CACHE_LOCATION)
        self.close()

    def __init__(self):
        Gtk.Window.__init__(self, title="Initial Setup")
        self.set_position(Gtk.WindowPosition.CENTER)
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.box1.set_border_width(10)
        self.cache = GtkFileChooser("Cache Location", config.CACHE_LOCATION)
        self.box1.pack_start(self.cache, False, True, 0)
        self.add(self.box1)
        self.font_dirs = []
        self.label = Gtk.Label()
        self.label.set_markup("<b>Font Directories</b>")
        self.label.set_alignment(0, 0)
        self.box1.pack_start(self.label, False, True, 0)
        self.addbutton = Gtk.Button.new_from_stock(Gtk.STOCK_ADD)
        self.addbutton.connect("clicked", self.add_chooser)
        self.box2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.box2.pack_start(self.addbutton, False, False, 0)
        self.okButton = Gtk.Button("Done")
        self.okButton.connect("clicked", self.finish)
        self.box2.pack_end(self.okButton, False, False, 0)
        self.box1.pack_end(self.box2, False, False, 0)

        for i in config.FONT_DIRS:
            self.add_chooser(i)

    def add_chooser(self, data):
        if data.__class__ == Gtk.Button:
            data = ""
        fc = RemovableGtkFileChooser("", data)
        self.font_dirs.append(fc)
        self.box1.pack_start(fc, False, False, 0)
        self.box1.show_all()


class GtkFontLoadingWindow(Gtk.Window):
    def __init__(self, thread):
        Gtk.Window.__init__(self)
        self.daemon_thread = thread
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_title("typecat")
        self.set_border_width(10)
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.label = Gtk.Label()
        self.label.set_markup("<b>Loading fonts</b>\nThis may take a few minutes, please wait...")
        self.label.set_alignment(0, 0)
        self.progressbar = Gtk.ProgressBar()
        self.current_font = Gtk.Label()
        self.current_font.set_alignment(0, 0)
        self.cancelbutton = Gtk.Button.new_from_stock(Gtk.STOCK_CANCEL)
        self.cancelbutton.set_halign(Gtk.Align.END)
        self.cancelbutton.connect("clicked", self.cancel)
        self.box1.pack_start(self.label, False, False, 0)
        self.box1.pack_start(self.progressbar, False, False, 0)
        self.box1.pack_start(self.current_font, False, False, 0)
        self.box1.pack_start(self.cancelbutton, False, False, 0)
        self.add(self.box1)

    def update_bar(self, upd):
        self.current_font.set_markup("<i>Loaded " + upd[1] + " from file</i>");
        self.progressbar.set_fraction(upd[0])
        self.show_all()

    def cancel(self, widget):
        setattr(self.daemon_thread, "stop_flag", True)
        self.destroy()
        Gtk.main_quit()

    def exit_handler(self, widget, event):
        self.cancel(widget)
