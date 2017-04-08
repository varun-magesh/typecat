from os.path import expanduser, isfile
from os import makedirs
# can't actually construct a tkinter font because you need a root window
SUBTITLE_FONT = "Helvetica 20 regular"
PIL_BACKGROUND = (255, 255, 239)
CACHE_LOCATION = expanduser("~/.types/")


def setup_cache():
    if not isfile(CACHE_LOCATION):
        makedirs(CACHE_LOCATION)


def heading_font(size=30):
    return "Helvetica {} bold".format(size)


def body_font(size=15):
    return "Helvetica {}".format(size)






