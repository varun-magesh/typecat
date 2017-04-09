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
    keys = list(fonts.keys())

NUM_LIST = 20

root = tk.Tk()
load_fonts()
info_panel = tk.Frame()

current_display = []


def show_info(font):
    global info_panel
    info_panel.grid_forget()
    del(info_panel)
    info_panel = fonts[font].display(500, 700)
    info_panel.configure(highlightbackground="#000000")
    # +1 for the top search bar
    info_panel.grid(row=0, column=0, sticky=tk.W+tk.N+tk.S, rowspan=NUM_LIST+1)


def generate_command(font):
    return lambda *args: show_info(font)
show_info("Libre Baskerville Regular")


def show_fonts(inputlist):
    """ Takes a list of string dict indices and displays them """
    global current_display
    for i in current_display:
        i.grid_forget()
    current_display = []
    for num, name in enumerate(inputlist):
        f = fonts[name].display(300, 25, root)
        f.configure(command=generate_command(name))
        # +1 for the search bar
        f.grid(column=1, row=num + 1, sticky=tk.E+tk.N+tk.W+tk.S, in_=root,
               padx=0, pady=0)
        current_display.append(f)


def search_fonts(strin):
    disp = []
    for i in keys:
        if strin.lower() in i.lower():
            disp.append(i)
    show_fonts(disp[:NUM_LIST])

# font size entry
sv1 = tk.StringVar()
sv1.trace("w", lambda n, idx, mode, sv=sv1:
          search_fonts(sv.get()))
sizein = tk.Entry(root, textvariable=sv1, width=3)
sizein.grid(sticky=tk.E+tk.N+tk.W, in_=root, row=0, column=1, padx=3, pady=3)
# root.geometry("1000x700")
show_fonts(keys[:NUM_LIST])

root.mainloop()
