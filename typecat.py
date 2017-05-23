from random import randint

from gi.repository import Gtk

import config
import manager

from display.configwindow import GtkConfigWindow
from display.fontboxbox import FontBoxBox
from display.fontbox import FontBox

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
#Initialize main font view
#root.add(fbb)

#load font files from cache
manager.load_cache()
manager.keys.sort(key=str.lower)

fbb = FontBoxBox()
fbb.refresh()
scrolled = Gtk.ScrolledWindow()
scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
scrolled.add(fbb)
root.add(scrolled)



def entry_callback(s):
    manager.search_fonts(s)
    #fontlist.refresh()

#fontlist.refresh()

root.show_all()
Gtk.main()
