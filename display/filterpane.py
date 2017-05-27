import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk
from font import Font


class FilterOption(Gtk.Box):
    def __init__(self, title, callback):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.checkbox = Gtk.CheckButton(title)
        self.feature = title
        self.adj = Gtk.Adjustment(0.0, -5.0, 5.0, 0.1, 0.5, 0)
        self.slider = Gtk.Scale(adjustment=self.adj, orientation=Gtk.Orientation.HORIZONTAL)
        self.slider.add_mark(0.0, Gtk.PositionType.BOTTOM)
        self.checkbox_state = self.checkbox.get_active()
        self.slider_value = self.slider.get_value()
        self.slider.set_draw_value(False)

        self.callback = callback

        self.checkbox.connect("toggled", self.on_click_checkbox)
        self.slider.connect("value-changed", self.on_move_slider)

        self.hseparator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)

        self.pack_start(self.checkbox, False, False, 0)
        self.pack_end(self.hseparator, True, True, 0)
        self.pack_end(self.slider, True, True, 0)

    def on_click_checkbox(self, button):
        self.checkbox_state = self.checkbox.get_active()
        self.callback()

    def on_move_slider(self, slider):
        self.slider_value = self.slider.get_value()
        if self.checkbox_state:
            self.callback()


class FilterPane(Gtk.Box):

    @staticmethod
    def sort_func(child1, child2, *user_data):
        return child2.font.dist() - child1.font.dist()
        if child1.font > child2.font:
            return -1
        if child1.font < child2.font:
            return 1
        if child1.font == child2.font:
            return 0

    def filter_(self, *args):
        Font.search_str = self.searchbar.get_text()
        for idx, fo in enumerate(self.filterwidgets):
            if fo.checkbox_state:
                Font.compare[idx][1] = fo.slider_value
            else:
                Font.compare[idx][1] = -1

        self.set_filter(FilterPane.sort_func)

    def __init__(self, set_filter):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_border_width(5)
        self.STYLE_PROPERTY_BORDER_STYLE = Gtk.BorderStyle.OUTSET
        self.filterwidgets = []
        self.set_filter = set_filter
        self.searchbar = Gtk.SearchEntry(valign=Gtk.Align.START)
        self.searchbar.connect("activate", self.filter_)
        print(self.searchbar.get_style_context().get_background_color(0))
        self.pack_start(self.searchbar, False, False, 0)
        for num, f in enumerate(Font.compare):
            fw = FilterOption(f[0], self.filter_)
            self.filterwidgets.append(fw)
            padding = 5
            if num == 0:
                padding = 10
            self.pack_start(fw, False, False, padding)
