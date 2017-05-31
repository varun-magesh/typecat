import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from typecat.font import Font


class FilterOption(Gtk.Box):
    def __init__(self, title, callback, update_on_move):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.checkbox = Gtk.CheckButton(title)
        self.feature = title
        self.update_on_move = update_on_move
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

        self.pack_start(self.hseparator, True, True, 0)
        self.pack_start(self.checkbox, False, False, 0)
        self.pack_end(self.slider, True, True, 0)

    def on_click_checkbox(self, button):
        self.checkbox_state = self.checkbox.get_active()
        self.callback()

    def on_move_slider(self, slider):
        self.slider_value = self.slider.get_value()
        if self.checkbox_state and self.update_on_move:
            self.callback()

class CategoryOption(Gtk.Box):
    def __init__(self, title, callback):
        Gtk.Box.__init__(self, orientation = Gtk.Orientation.HORIZONTAL, spacing=6)
        self.checkbox = Gtk.CheckButton(title)
        self.callback = callback
        self.feature = title
        self.pack_start(self.checkbox, False, False, 0)
        self.checkbox.set_halign(Gtk.Align.START)
        self.checkbox_state = self.checkbox.get_active()

    def on_click_checkbox(self, button):
        self.checkbox_state = self.checkbox.get_active()
        self.callback()



class FilterPane(Gtk.Box):

    @staticmethod
    def sort_func(child1, child2, *user_data):
        return child2.font.dist() - child1.font.dist()

    def filter_(self, *args):
        Font.search_str = self.searchbar.get_text()
        for fo in self.filterwidgets:
            if fo.checkbox_state:
                Font.compare[fo.feature.lower().replace(" ", "_")] = fo.slider_value
            else:
                Font.compare[fo.feature.lower().replace(" ", "_")] = -1

        Font.search_categories = []
        for co in self.categorywidgets:
            if co.checkbox_state:
                Font.search_categories.append(co.feature.upper())

        self.set_filter(FilterPane.sort_func)

    def __init__(self, set_filter):
        Gtk.Box.__init__(self, orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_border_width(5)
        self.STYLE_PROPERTY_BORDER_STYLE = Gtk.BorderStyle.OUTSET
        self.filterwidgets = []
        self.categorywidgets = []
        self.set_filter = set_filter
        self.searchbar = Gtk.SearchEntry(valign=Gtk.Align.START)
        self.searchbar.connect("activate", self.filter_)
        self.searchbar.set_margin_bottom(15)
        self.pack_start(self.searchbar, False, False, 0)
        for f in Font.compare.keys():
            if len(Font.fonts) > 200:
                fw = FilterOption(f.replace("_", " ").title(), lambda *x: 0, False)
            else:
                fw = FilterOption(f.replace("_", " ").title(), self.filter_, True)
            self.filterwidgets.append(fw)
            padding = 5
            self.pack_start(fw, False, False, padding)
        for c in Font.CATEGORIES.keys():
            if type(c) is int or c.isdigit():
                continue
            cw = CategoryOption(c.title(), self.filter_)
            self.categorywidgets.append(cw)
            self.pack_start(cw, False, False, 5)


        if len(Font.fonts) > 200:
            self.button = Gtk.Button.new_with_label("Sort")
            self.button.connect("clicked", self.filter_)
            self.pack_start(self.button, False, False, 0)
            self.show_all()


