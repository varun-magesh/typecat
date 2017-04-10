from os.path import expanduser, isfile
from os import makedirs
from sys import platform as _platform
# can't actually construct a tkinter font because you need a root window
PIL_BACKGROUND = (255, 255, 239)
CACHE_LOCATION = expanduser("~/.types/")
FONT_DIRS = []
if _platform == "linux" or _platform == "linux2":
	FONT_DIRS = [expanduser("~/.fonts"), "/usr/share/fonts"]
elif _platform == "darwin":
	FONT_DIRS = [expanduser("~/Library/Fonts"), "/Library/Fonts", " /System/Library/Fonts"]
elif _platform == "win32":
	print("According to superuser.com, C:\\Windows\\Fonts is a symlink to something in SxS. Python should follow the symlink right though. If all you see is this message and nothing else like 'Loaded font from...' then it didn't.")
	FONT_DIRS = ["C:\\Windows\\Fonts"]
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
