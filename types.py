from font import Font
import tkinter as tk
import pickle
import os
import config

fonts = dict()
keys = list()

def load_fonts():
    # TODO if you have a lot of fonts this might kill memory, we should load and
    # del fonts as necessary.
    cachedfonts = os.listdir(config.CACHE_LOCATION)
    for f in cachedfonts:
        fontname = f[:-7].replace("_", " ")
        fonts[fontname] = pickle.load(open("{}/{}".format(
                                    config.CACHE_LOCATION, f), "rb"))
        print("Loaded {} from cache".format(fonts[fontname].name))

    for fontdir in config.FONT_DIRS:
        for dirpath, dirnames, filenames in os.walk(fontdir):
            for d in filenames:
                idx = d.rfind(".")
                if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                    fontname = ""
                    try:
                        fontname = Font.extract_name(os.path.join(dirpath, d))
                        if fontname not in fonts:
                            print(os.path.join(dirpath, d))
                            f = Font(os.path.join(dirpath, d))
                            fonts[fontname] = f
                    except:
                        print("Failed to read font at path {}".format(
                                      os.path.join(dirpath, d)))


root = tk.Tk()
load_fonts()
w = fonts["Libre Baskerville Regular"].display(500, 700)
w.configure(highlightbackground="#000000")
w.grid(row=0, column=0, sticky=tk.W)
root.geometry("700x1000")
root.mainloop()
