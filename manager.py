import pickle
import os
import config
import statistics
from math import sqrt

keys = list()
fonts = dict()

COMPARABLE_FEATURES = ["slant", "thickness", "width", "height",
                       "ratio", "thickness_variation"]


def load_cache():
    # TODO if you have a lot of fonts this might kill memory, we should load and
    # del fonts as necessary.
    cachedfonts = os.listdir(config.CACHE_LOCATION)
    for f in cachedfonts:
        fontname = f[:-7]
        fonts[fontname] = pickle.load(open("{}/{}".format(
                                    config.CACHE_LOCATION, f), "rb"))
        print("Loaded {} from cache".format(fonts[fontname].name))
    global keys
    keys = list(fonts.keys())


def load_files():
    for fontdir in config.FONT_DIRS:
        for dirpath, dirnames, filenames in os.walk(fontdir):
            for d in filenames:
                idx = d.rfind(".")
                if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                    try:
                        fontname = Font.extract_name(os.path.join(dirpath, d))
                        if fontname not in fonts:
                            g = Font(os.path.join(dirpath, d))
                            fonts[fontname] = g
                            g.save()
                    except Exception:
                        print("Failed to read font at path {}".format(
                                      os.path.join(dirpath, d)))
    global keys
    keys = list(fonts.keys())


def load_fonts():
    load_cache()
    load_files()


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
                total += abs(scale(f, (v - fonts[vals].__dict__[f])**2))
            else:
                total += 0 if v == fonts[vals].__dict__[f] else 1
        return sqrt(total)
    keys.sort(key=sortkey)


def search_fonts(searchstr):
    def sortkey(vals):
        return 0 if searchstr.lower() in vals.lower() else 1
    keys.sort(key=sortkey)
