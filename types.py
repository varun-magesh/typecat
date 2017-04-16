from random import randint
import tkinter as tk
import manager
import config
from typesdisplay import FilterOption

root = tk.Tk()
manager.load_fonts()
manager.keys.sort(key=str.lower)
info_panel = tk.Frame()

current_display = []


def show_info(font):

    info_panel = manager.fonts[font].display(500, 700)
    info_panel.grid_propagate(0)
    info_panel.configure(highlightbackground="#000000")
    # +1 for the top search bar
    info_panel.grid(row=0, column=0, sticky=tk.W+tk.N+tk.S, rowspan=NUM_LIST+1)


optionwidgets = []
def find_options():
    features = []
    values = []
    for ow in optionwidgets:
        if ow.checkbutton_state:
            features.append(ow.feature)
            map_stdev = ow.slider_state * config.SCALE[ow.feature][1] + \
                config.SCALE[ow.feature][0]
            values.append(map_stdev)
    manager.find_features(features, values)
    show_fonts(manager.keys[:NUM_LIST])
for num, f in enumerate(manager.COMPARABLE_FEATURES):
    p = FilterOption(root, f, find_options)
    optionwidgets.append(p)
    p.grid(column=1 if num % 2 == 0 else 2, row=int(.5*num)+1,
           sticky=tk.N+tk.W, in_=root, padx=0, pady=0)

show_info(manager.keys[randint(0, len(manager.keys) - 1)])


def entry_callback(s):
    manager.search_fonts(s)
    show_fonts(manager.keys[:NUM_LIST])

sv1 = tk.StringVar()
sv1.trace("w", lambda n, idx, mode, sv=sv1:
          entry_callback(sv.get()))
sizein = tk.Entry(root, textvariable=sv1, width=64)
sizein.grid_propagate(0)
sizein.grid(sticky=tk.E+tk.N+tk.W, in_=root, row=0, column=1, padx=3, pady=3,
            columnspan=2)
root.geometry("1030x700")
show_fonts(manager.keys[:NUM_LIST])
root.grid_propagate(0)

root.mainloop()
