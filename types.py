from random import randint
import tkinter as tk
import manager
from display.filteroption import OptionFrame
from display.fontlist import FontList
from display.infopanel import InfoPanel

root = tk.Tk()
manager.load_cache()
manager.keys.sort(key=str.lower)
info_panel = tk.Frame()

current_display = []

def show_info(font):
    info_panel = InfoPanel(font)
    info_panel.grid_propagate(0)
    # +1 for the top search bar
    info_panel.grid(row=0, column=0, sticky=tk.W+tk.N+tk.S, rowspan=4)


show_info(manager.keys[randint(0, len(manager.keys) - 1)])

fontlist = FontList(show_info)
optionframe = OptionFrame(fontlist.refresh)

fontlist.grid(row=2, column=1, sticky=tk.W+tk.N+tk.S+tk.E)
optionframe.grid(row=1, column=1, sticky=tk.W+tk.N+tk.S+tk.E)


def entry_callback(s):
    manager.search_fonts(s)
    fontlist.refresh()

sv1 = tk.StringVar()
sv1.trace("w", lambda n, idx, mode, sv=sv1:
          entry_callback(sv.get()))
sizein = tk.Entry(root, textvariable=sv1, width=64)
sizein.grid_propagate(0)
sizein.grid(sticky=tk.E+tk.N+tk.W, in_=root, row=0, column=1, padx=3, pady=3,
            columnspan=2)
root.geometry("1030x700")
fontlist.refresh()
root.grid_propagate(0)

root.mainloop()
