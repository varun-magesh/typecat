import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import config
import manager

from display.configwindow import GtkConfigWindow
from display.fontboxbox import FontBoxBox
from display.filterpane import FilterPane

#Check if we need to do first time setup
if not config.read_config():
        cw = GtkConfigWindow()
        cw.show_all()
        cw.connect("delete-event", Gtk.main_quit)
        Gtk.main()
        manager.load_files()

#Initialize window and grid
root = Gtk.Window()
root.connect("delete-event", Gtk.main_quit)
grid = Gtk.Grid()
root.add(grid)
#Initialize main font view
#root.add(fbb)

#load font files from cache
manager.load_cache()
manager.keys.sort(key=str.lower)

fbb = FontBoxBox()
fp = FilterPane(fbb.set_sort_func)
grid.add(fp)
grid.attach(fbb, 1, 0, 1, 1)
grid.set_border_width(5)

root.show_all()
Gtk.main()
