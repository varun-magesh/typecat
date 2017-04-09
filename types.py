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
        fontname = f[:-7]
        fonts[fontname] = pickle.load(open("{}/{}".format(
                                    config.CACHE_LOCATION, f), "rb"))
        print("Loaded {} from cache".format(fonts[fontname].name))

    for fontdir in config.FONT_DIRS:
        for dirpath, dirnames, filenames in os.walk(fontdir):
            for d in filenames:
                idx = d.rfind(".")
                if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                    try:
                        fontname = Font.extract_name(os.path.join(dirpath, d))
                        if fontname not in fonts:
                            g = Font(os.path.join(dirpath, d))
                            fonts[fontname] = f
                            g.save()
                    except TypeError:
                        print("Failed to read font at path {}".format(
                                      os.path.join(dirpath, d)))
    global keys
    keys = fonts.keys()


root = tk.Tk()
load_fonts()
w = fonts["Libre Baskerville Regular"].display(500, 700)
w.configure(highlightbackground="#000000")
w.grid(row=0, column=0, sticky=tk.W+tk.N+tk.S)
for num, font in enumerate(keys):
    if num >= 10:
        break
    f = fonts[font].display(300, 200)
    f.grid(row=0, sticky=tk.E, in_=root)
root.geometry("1000x700")
root.mainloop()
