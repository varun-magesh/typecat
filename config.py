from os.path import expanduser, isfile
from os import makedirs
# can't actually construct a tkinter font because you need a root window
PIL_BACKGROUND = (255, 255, 239)
CACHE_LOCATION = expanduser("~/.types/")
FONT_DIRS = [expanduser("~/.fonts"), "/usr/share/fonts"]
FONT_FILE_EXTENSIONS = [".ttf", ".otf"]
# all scales are at size 50
# Mean, Stddev
SCALE = {}
SCALE["ascent"] = (43.492, 6.1676)
SCALE["descent"] = (14.3301, 4.207)
SCALE["height"] = (45.2006, 6.62049)
SCALE["width"] = (30.3181818, 4.2233)
SCALE["ratio"] = (1.51656, 0.28923)
SCALE["thickness"] = (3.620056, 1.0616)
SCALE["thickness_variation"] = (1.7069, 0.7979866)
SCALE["slant"] = (.0596753, 0.0953168)


def setup_cache():
    if not isfile(CACHE_LOCATION):
        makedirs(CACHE_LOCATION)


def heading_font(size=30):
    return "Helvetica {} bold".format(size)


def body_font(size=15):
    return "Helvetica {}".format(size)
