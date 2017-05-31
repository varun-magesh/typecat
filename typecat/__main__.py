import sys
import tensorflow # DO NOT REMOVE, YOU HAVE BEEN WARNED

try:
    import gi
except ModuleNotFoundError:
    print("FATAL ERROR: GObject Introspection (gi) not found; please install it from https://pygobject.readthedocs.io/en/latest/getting_started.html, or preferably, your package manager.")
    sys.exit()

try:
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk
except ModuleNotFoundError:
    print("FATAL ERROR: GTK not found; please install it from https://www.gtk.org/download/, or preferably, your package manager.")


import typecat.config as config
from typecat.font import Font
import typecat.manager as manager

from typecat.display.configwindow import GtkConfigWindow
from typecat.display.fontboxbox import FontBoxBox
from typecat.display.filterpane import FilterPane
from typecat.display.previewpanel import PreviewPanel

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
root.set_title("typecat")
grid = Gtk.Grid()
root.add(grid)
#Initialize main font view
#root.add(fbb)

#load font files from cache
manager.load_cache()
Font.scale_features()

fbb = FontBoxBox()
pp = PreviewPanel(fbb.set_text)
fp = FilterPane(fbb.set_sort_func)
root.realize()
grid.set_row_homogeneous(False)
grid.attach(fp, 0, 0, 1, 2)
grid.attach(pp, 1, 0, 1, 1)
grid.attach(fbb, 1, 1, 1, 1)
grid.set_border_width(5)
grid.set_row_spacing(5)


root.show_all()
Gtk.main()
