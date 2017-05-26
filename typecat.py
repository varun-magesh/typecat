import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

import config
import manager
import font

from display.configwindow import GtkConfigWindow
from display.fontboxbox import FontBoxBox
from display.filterpane import FilterPane
from display.previewpanel import PreviewPanel

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
font.scale_features()

fbb = FontBoxBox()
pp = PreviewPanel()
fp = FilterPane(fbb.set_sort_func)
grid.set_row_homogeneous(False)
grid.attach(fp, 0, 0, 1, 2)
grid.attach(pp, 1, 0, 1, 1)
grid.attach(fbb, 1, 1, 1, 1)
grid.set_border_width(5)
grid.set_row_spacing(5)

root.show_all()
Gtk.main()
