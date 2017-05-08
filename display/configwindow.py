import gi
import tkinter as tk
import config
import tkinter.filedialog as fd
from os.path import isdir
import manager
from os import mkdir
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class FileChooser(tk.Frame):

    def __init__(self, root, title, default):
        super().__init__(root)
        if not title == "":
            cachetitle = tk.Label(self, text=title)
            cachetitle.grid(sticky=tk.W, row=0, column=0)

        self.svtext = tk.StringVar()
        if len(default) > 0 and default[-1] != "/":
            default += "/"
        print(default)

        path = tk.Entry(self, textvariable=self.svtext, width=50)
        path.insert(0, default)
        path.grid(row=1, column=0, padx=5)

        def set_dir():
            self.cache = fd.askdirectory()
            self.svtext.set(self.cache)

        files = tk.Button(self, text="Browse", command=set_dir)
        files.grid(row=1, column=1, padx=2, pady=2)

    def get_file(self):
        return self.svtext.get()

class GtkFileChooser(Gtk.Box):
    def __init__(self, title, defaultPath):
        builder = Gtk.Builder()

        builder.add_from_file("filechooser.glade")
        with builder.get_object as b:
            b("pathdesc").set_text(title)
            b("pathbox").set_text(defaultPath)
            b("browsebutton").connect("clicked", self.openBrowser(b("pathbox")))

            def openBrowser(textfield):
                dialog = Gtk.FileChooserDialog("Choose a directory", self,
                                               Gtk.FileChooserAction.SELECT_FOLDER,
                                               (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                                "Select", Gtk.ResponseType.OK))
                dialog.set_default_size(800, 400)
                resp = dialog.run()
                if resp == Gtk.ResponseType.OK:
                    textfield.set_text(dialog.get_filename())
            def get_file(self):
                return b("pathbox").get_text()



class RemovableFileChooser(tk.Frame):

    def __init__(self, root, title, default):
        super().__init__(root)
        self.fc = FileChooser(self, title, default)
        self.fc.grid()
        butt = tk.Button(self, text="X", command=self.grid_forget)
        butt.grid(column=1, row=0)

    def get_file(self):
        return self.fc.get_file()


class ConfigWindow(tk.Frame):

    def finish(self):
        config.CACHE_LOCATION = self.cache.get_file()
        config.FONT_DIRS = []
        for i in self.font_dirs:
            if i.get_file() != "":
                config.FONT_DIRS.append(i.get_file())
        if not isdir(config.CACHE_LOCATION):
            mkdir(config.CACHE_LOCATION)
        manager.load_files()
        self.exit()

    def __init__(self, root, exit):
        super().__init__(root)

        self.cache = FileChooser(self, "Cache Location", config.CACHE_LOCATION)
        self.cache.grid(sticky=tk.W)
        self.font_dirs = []
        self.exit = exit
        dirs = tk.Label(self, text="Font Directories")
        dirs.grid(sticky=tk.W)

        addbutton = tk.Button(self, text="+")
        okbutton = tk.Button(self, text="OK", command=self.finish)
        okbutton.grid(row=self.grid_size()[1])

        def add_rfc(filename=""):
            fc = RemovableFileChooser(self, "", filename)
            self.font_dirs.append(fc)
            fc.grid(padx=5, pady=0)
            addbutton.grid(sticky=tk.E+tk.W, row=self.grid_size()[1], padx=5)
            okbutton.grid(row=self.grid_size()[1], pady=5, padx=10)

        for i in config.FONT_DIRS:
            add_rfc(i)

        addbutton.configure(command=add_rfc)
