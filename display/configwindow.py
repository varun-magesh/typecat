import tkinter as tk
import config
import tkinter.filedialog as fd


class FileChooser(tk.Frame):

    def __init__(self, root, title, default):
        super().__init__(root)
        if not title == "":
            cachetitle = tk.Label(self, text=title)
            cachetitle.grid(sticky=tk.W, row=0, column=0)

        self.svtext = tk.StringVar()
        self.svtext.set(default)

        path = tk.Entry(self, textvariable=self.svtext)
        path.insert(0, default)
        path.grid(row=1, column=0)

        def set_dir():
            self.cache = fd.askdirectory()
            self.svtext.set(self.cache)

        files = tk.Button(self, text="Browse", command=set_dir)
        files.grid(row=1, column=1)

    def get_file(self):
        return self.svtext.get()


class RemovableFileChooser(tk.Frame):

    def __init__(self, root, title, default):
        super().__init__(root)
        fc = FileChooser(self, title, default)
        fc.grid()
        butt = tk.Button(self, text="X", command=self.grid_forget)
        butt.grid(column=1, row=0)


class ConfigWindow(tk.Frame):

    def __init__(self, root, exit):
        super().__init__(root)

        self.cache = FileChooser(self, "Cache Location", config.CACHE_LOCATION)
        self.cache.grid(sticky=tk.W)
        self.font_dirs = []
        dirs = tk.Label(self, text="Font Directories")
        dirs.grid(sticky=tk.W)

        addbutton = tk.Button(self, text="+")
        okbutton = tk.Button(self, text="OK", command=exit)
        okbutton.grid(row=self.grid_size()[1])

        def add_rfc(filename=""):
            fc = RemovableFileChooser(self, "", filename)
            self.font_dirs.append(fc)
            fc.grid()
            addbutton.grid(sticky=tk.E+tk.W, row=self.grid_size()[1])
            okbutton.grid(row=self.grid_size()[1])

        for i in config.FONT_DIRS:
            add_rfc(i)

        addbutton.configure(command=add_rfc)
