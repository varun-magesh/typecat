from random import randint
import tkinter as tk
import manager
from display.filteroption import OptionFrame
from display.fontlist import FontList
from display.infopanel import InfoPanel
from display.searchbar import SearchBar
from display.configwindow import GtkConfigWindow
from gi.repository import Gtk
import config


if not config.read_config():
    print("opening cw")
    cw = GtkConfigWindow()
    cw.show_all()
    cw.connect("delete-event", Gtk.main_quit)
    Gtk.main()

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

fontlist = FontList(show_info, pady=5, padx=3)
optionframe = OptionFrame(fontlist.refresh)

fontlist.grid(row=2, column=1, sticky=tk.W+tk.N+tk.S+tk.E)
optionframe.grid(row=1, column=1, sticky=tk.W+tk.N+tk.S+tk.E)

menubar = tk.Menu(root)
root.config(menu=menubar)
filemenu = tk.Menu(menubar)
menubar.add_cascade(label='File', menu=filemenu)
menubar.add_command(label='Reload', command=manager.load_files)


filemenu.add_command(label='Settings', command=None)
filemenu.add_command(label='Refresh Font Files from Path', command=None)
filemenu.add_separator()


def entry_callback(s):
    manager.search_fonts(s)
    fontlist.refresh()

sizein = SearchBar(root, entry_callback, width=64)
sizein.grid_propagate(0)
sizein.grid(sticky=tk.E+tk.N+tk.W, in_=root, row=0, column=1, padx=3, pady=3,
            columnspan=2)

fontlist.refresh()

root.geometry("1033x700")
root.grid_propagate(0)
root.mainloop()
