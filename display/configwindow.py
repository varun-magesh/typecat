import tkinter as tk
import config
import tkinter.filedialog as fd
from os.path import isdir
from os import mkdir


class FileChooser(tk.Frame):

    def __init__(self, root, title, default):
        super().__init__(root)
        if not title == "":
            cachetitle = tk.Label(self, text=title)
            cachetitle.grid(sticky=tk.W, row=0, column=0)

        self.svtext = tk.StringVar()
        if default[-1] != "/":
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
