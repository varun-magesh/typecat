import pickle
import os
import config
import statistics
from math import sqrt
from font import RenderError, Font
from display.configwindow import GtkFontLoadingWindow
from gi.repository import GLib, GObject, Gtk
import threading

keys = list()
fonts = dict()
exceptions = set()

COMPARABLE_FEATURES = ["slant", "thickness", "width", "height",
                       "ratio", "thickness_variation"]

total_files = 0
loaded_files = 0
current_file_name = ""
total_cache = 0
loaded_cache = 0


def load_cache():
    # TODO if you have a lot of fonts this might kill memory, we should load and
    # del fonts as necessary.
    global exceptions
    try:
        exceptions = pickle.load(open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "rb"))
    except pickle.PickleError:
        print("Exception file not found, initializing blank one")
    global total_cache, loaded_cache
    cachedfonts = os.listdir(config.CACHE_LOCATION)
    total_cache = len(cachedfonts)
    for f in cachedfonts:
        if f[-7:] != ".pickle" or f[-7:] in exceptions:
            print("File {} is in exception list".format(f))
            continue
        fontname = f[:-7]
        try:
            loadfont = pickle.load(open("{}/{}".format(
                config.CACHE_LOCATION, f), "rb"))
            fonts[fontname] = loadfont
            print("Loaded {} from cache".format(fonts[fontname].name))
        except RenderError:
            print("Skipping {}, unable to render correctly, adding to exceptions".format(fontname))
            exceptions.add(fontname)
        loaded_cache += 1
    global keys
    keys = list(fonts.keys())
    pickle.dump(exceptions, open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "wb"))




def load_files():
    def run():
        t = threading.currentThread()

        fontpaths = []
        global total_files, loaded_files, current_file_name, exceptions
        try:
            exceptions = pickle.load(open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "rb"))
        except pickle.PickleError:
            print("Exception file not found, initializing blank one")
        for fontdir in config.FONT_DIRS:
            for dirpath, dirnames, filenames in os.walk(fontdir):
                for d in filenames:
                    idx = d.rfind(".")
                    if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                        fontpaths.append(os.path.join(dirpath, d))
        total_files = len(fontpaths)

        for f in fontpaths:
            try:
                fontname = Font.extract_name(f)
                current_file_name = fontname
                if fontname in exceptions or f in exceptions:
                    print("Skipping font {}, in exception list".format(fontname))
                    continue
                g = Font(f)
                fonts[fontname] = g
                g.save()
                print("Loaded {} from file".format(
                    g.name))
            except Exception as e:
                print(("Failed to read font at path {}"
                       "with exception {}").format(
                    f, e))
                exceptions.add(f)
                pickle.dump(exceptions, open("{}/exceptions.tcat".format(config.CACHE_LOCATION), "wb"))

            loaded_files += 1
            GLib.idle_add(win.update_bar, [float(loaded_files / total_files), current_file_name])

            if getattr(t, "stop_flag", True):
                break
            if loaded_files == total_files:
                GLib.idle_add(win.cancel, None)

    thread = threading.Thread(target=run)
    setattr(thread, "stop_flag", False)
    thread.daemon = True
    win = GtkFontLoadingWindow(thread)
    win.connect("delete-event", win.exit_handler)
    win.show_all()
    GObject.threads_init()
    thread.start()
    Gtk.main()
    thread.join()

    global keys
    keys = list(fonts.keys())


def load_fonts():
    load_cache()
    load_files()

# def update_cache():
#     for fontdir in config.FONT_DIRS:
#         for dirpath, dirnames, filenames


def scale(feature, value):
    """ Scales a value to its standard dev. across the font set. """
    return (config.SCALE[feature][0] - value) / config.SCALE[feature][1]


def scale_features():
    """
    Calculates the stddev and mean of each feature.
    Not necessary to be run more than once in a while.
    I might end up pasting the scales from my own fonts into the code, should
    be just fine.
    """
    for f in COMPARABLE_FEATURES:
        population = []
        for k in keys:
            population.append(fonts[k].__dict__[f])
        mean = sum(population) / max(len(population), 1)
        stddev = statistics.pstdev(population)
        print("Feature {} Mean {} Standard Dev. {}".format(f, mean, stddev))


def find_features(features, values):
    def sortkey(vals):
        total = 0
        for v, f in zip(values, features):
            if type(v) in [float, int]:
                # TODO feature scaling
                total += abs(scale(f, (v - fonts[vals].__dict__[f]) ** 2))
            else:
                total += 0 if v == fonts[vals].__dict__[f] else 1
        return sqrt(total)

    keys.sort(key=sortkey)


def search_fonts(searchstr):
    def sortkey(vals):
        return 0 if searchstr.lower() in vals.lower() else 1

    keys.sort(key=sortkey)
