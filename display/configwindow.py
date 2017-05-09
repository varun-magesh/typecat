import gi
import tkinter as tk
import config
import tkinter.filedialog as fd
from os.path import isdir
import manager
from os import mkdir

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class GtkFileChooser(Gtk.Box):
    def __init__(self, title, default):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.pathdesc = Gtk.Label()
        self.pathdesc.set_markup("<b>" + title + "</b>")
        self.entrybox = Gtk.Entry()
        self.entrybox.set_text(default)
        self.browsebutton = Gtk.Button("Browse")
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.pack_start(self.pathdesc, False, False, 0)
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
        self.fc.box1.pack_end(removebutt, True, True, 0)
        removebutt.connect("clicked", self.killme)

    def killme(self, button):
        self.destroy()

    def get_file(self):
        return self.fc.get_file()


class GtkConfigWindow(Gtk.Window):
    def finish(self):
        config.CACHE_LOCATION = self.cache.get_file()
        config.FONT_DIRS = []
        for i in self.font_dirs:
            if i.get_file() != "":
                config.FONT_DIRS.append(i.get_file())
        if not isdir(config.CACHE_LOCATION):
            mkdir(config.CACHE_LOCATION)
        manager.load_files()
        self.close()

    def __init__(self):
        Gtk.Window.__init__(self, title="Initial Setup")
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.cache = GtkFileChooser(self, "Cache Location", config.CACHE_LOCATION)
        self.box1.pack_start(self.cache, True, True, 0)
        self.add(self.box1)
        self.font_dirs = []
        self.label = Gtk.Label.set_markup("<b>Font Directories</b>")
        self.label.set_alignment(xscale=0)
        self.box1.pack_end(self.label, True, True, 0)
        addbutton = Gtk.Button("Add more:")
        addbutton.connect("clicked")
        okButton = Gtk.Button("Done")
        okButton.connect("clicked", self.finish)


win = Gtk.Window()
win.add(RemovableGtkFileChooser("hey", "hey"))
win.show_all()
win.connect("delete-event", Gtk.main_quit)
Gtk.main()


# class ConfigWindow(tk.Frame):
#     def finish(self):
#         config.CACHE_LOCATION = self.cache.get_file()
#         config.FONT_DIRS = []
#         for i in self.font_dirs:
#             if i.get_file() != "":
#                 config.FONT_DIRS.append(i.get_file())
#         if not isdir(config.CACHE_LOCATION):
#             mkdir(config.CACHE_LOCATION)
#         manager.load_files()
#         self.exit()
#
#     def __init__(self, root, exit):
#         super().__init__(root)
#
#         self.cache = FileChooser(self, "Cache Location", config.CACHE_LOCATION)
#         self.cache.grid(sticky=tk.W)
#         self.font_dirs = []
#         self.exit = exit
#         dirs = tk.Label(self, text="Font Directories")
#         dirs.grid(sticky=tk.W)
#
#         addbutton = tk.Button(self, text="+")
#         okbutton = tk.Button(self, text="OK", command=self.finish)
#         okbutton.grid(row=self.grid_size()[1])
#
#         def add_rfc(filename=""):
#             fc = RemovableFileChooser(self, "", filename)
#             self.font_dirs.append(fc)
#             fc.grid(padx=5, pady=0)
#             addbutton.grid(sticky=tk.E + tk.W, row=self.grid_size()[1], padx=5)
#             okbutton.grid(row=self.grid_size()[1], pady=5, padx=10)
#
#         for i in config.FONT_DIRS:
#             add_rfc(i)
#
#         addbutton.configure(command=add_rfc)
#
# class FileChooser(tk.Frame):
#     def __init__(self, root, title, default):
#         super().__init__(root)
#         if not title == "":
#             cachetitle = tk.Label(self, text=title)
#             cachetitle.grid(sticky=tk.W, row=0, column=0)
#
#         self.svtext = tk.StringVar()
#         if len(default) > 0 and default[-1] != "/":
#             default += "/"
#         print(default)
#
#         path = tk.Entry(self, textvariable=self.svtext, width=50)
#         path.insert(0, default)
#         path.grid(row=1, column=0, padx=5)
#
#         def set_dir():
#             self.cache = fd.askdirectory()
#             self.svtext.set(self.cache)
#
#         files = tk.Button(self, text="Browse", command=set_dir)
#         files.grid(row=1, column=1, padx=2, pady=2)
#
#     def get_file(self):
#         return self.svtext.get()
#
# class RemovableFileChooser(tk.Frame):
#     def __init__(self, root, title, default):
#         super().__init__(root)
#         self.fc = FileChooser(self, title, default)
#         self.fc.grid()
#         butt = tk.Button(self, text="X", command=self.grid_forget)
#         butt.grid(column=1, row=0)
#
#     def get_file(self):
#         return self.fc.get_file()
