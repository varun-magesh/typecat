"""
The Font class extracts and stores image data from font files.
It is constructed with a path to a .ttf or .otf file and automatically extracts
visual features.
It also stores some static information on font sorting and categorization.
It also automatically scales font features to uniform values for easier sorting.
"""
from PIL import ImageFont, ImageStat
import typecat.config as config
import typecat.font2img as f2i
import numpy as np
from math import sqrt
import pickle
from io import StringIO
import tensorflow as tf
from pkg_resources import resource_string

#mean stddev min max
_MEAN = 0
_STDDEV = 1
_MIN = 2
_MAX = 3

#setup tf model
_FIVE_CLASS_MODEL = resource_string(__name__, 'models/five_class_graph.pb')

GRAPH = tf.GraphDef()
GRAPH.ParseFromString(_FIVE_CLASS_MODEL)
_ = tf.import_graph_def(GRAPH, name='')


class RenderError(Exception):
    """ Error thrown when a font renders as boxes """
    pass

class Font(object):
    """
    Stores cached information about fonts in memory.
    Attributes:
        name
        family
        path
        pilfont: PIL font object
        size: current font size
        category: serif, sans, display, etc.
        languages
        thicknesses: the thickness values at all points in the typeface
        thickness: average thickness
        thickness_variation: standard dev. of thicknesses
        slant
        width
        height
        ratio: height/width
        style: bold, thin, italic etc.
        ascent: space between lowercase height and uppercase height
        descent: length of tail on 'p', 'q', and others
    """

    ALPHABET = "abcdefghijklmnopqrstuvwxyz"

    CATEGORIES = {
        "SERIF": 0,
        "HANDWRITING": 1,
        "DISPLAY": 2,
        "MONOSPACE": 3,
        "SANS": 4,
        0: "SERIF",
        1: "HANDWRITING",
        2: "DISPLAY",
        3: "MONOSPACE",
        4: "SANS",
    }

    compare = {
        "slant": -6,
        "thickness": -6,
        "width": -6,
        "height": -6,
        "ascent": -6,
        "descent": -6,
    }

    FIVE_CLASS_MODEL = _FIVE_CLASS_MODEL

    """ String user is searching for if any """
    search_str = ""
    """ Categories checked """
    search_categories = []
    """ All fonts loaded key=name value=Font object """
    fonts = dict()
    """ feature scaling stat values, key=feature value=(mean, stddev, max, min)"""
    scale_values = dict()

    # pylint: disable=too-many-instance-attributes
    # Fonts have a lot of data to store

    def dist(self):
        """
        Calculates the Euclidean distance between this font and the user's
        specifications so it can be sorted in fontboxbox
        Relies heavily upon feature scaling.
        """
        total = 0
        if self.category in Font.search_categories:
            total += 1000
        if Font.search_str != "" and Font.search_str.lower() in self.name.lower():
            total += 100
        for feature, setting in Font.compare.items():
            if setting == -6:
                # Setting is not being used
                continue
            if isinstance(setting, (float, int)):
                total += (setting - Font.scale(feature,
                                               self.__dict__[feature])) ** 2
            else:
                total += 0 if setting == self.__dict__[feature] else 1
        return sqrt(total)

    def __lt__(self, other):
        return self.dist() < other.dist()

    def __gt__(self, other):
        return self.dist() > other.dist()

    def __eq__(self, other):
        return self.dist() == other.dist()

    def __ne__(self, other):
        return self.dist() != other.dist()

    def __init__(self, arg1, arg2=None):
        # option 1: a path to a font to go find the details yourself
        if isinstance(arg1, str):
            self.path = arg1
            if arg2 is not None:
                self.size = arg2
            else:
                self.size = 50
            self.open_path()

            self.extract_PIL()
            self.extract_width()
            self.extract_thickness()
            self.extract_category()
            self.extract_slant()

            print("Loaded {} from {}".format(self.name, self.path))

    def open_path(self):
        self.pilfont = ImageFont.truetype(self.path, size=self.size)
        a = f2i.single_pil("A", self.pilfont, fore=1, back=0)[0]
        b = f2i.single_pil("B", self.pilfont, fore=1, back=0)[0]
        if a == b:
            print("Could not render {} properly.".format(self.name))
            raise RenderError("Could not render {} properly.".format(self.name))

    def extract_PIL(self):
        """ Extracts all data already collected by PIL fonts """
        self.family = self.pilfont.font.family
        self.style = self.pilfont.font.style
        self.name = "{} {}".format(self.family, self.style)
        self.ascent = self.pilfont.font.ascent
        self.descent = self.pilfont.font.descent

    def extract_width(self):
        """ Infers width by averaging individual character widths. """
        totalwidth = 0
        totalheight = 0
        fullabc = Font.ALPHABET + Font.ALPHABET.upper()
        for c in list(fullabc):
            img, draw = f2i.single_pil(c, self.pilfont, fore=1, back=0)
            bbox = img.getbbox()
            totalwidth += bbox[2] - bbox[0]
            totalheight += bbox[3] - bbox[1]
        self.height = totalheight / len(fullabc)
        self.width = totalwidth / len(fullabc)

    def extract_thickness(self):
        """
        Calculates thickness by averaging dark bits
        """
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        img = f2i.single_pil(slstr, self.pilfont)[0]
        self.thickness = ImageStat.mean(img)

    def getsize(self, *args):
        return self.pilfont.getsize(*args)

    def extract_category(self):
        img = self.training_img()
        f = StringIO()
        img.save(f, 'JPEG')
        image_data = tf.gfile.FastGFile(f, 'rb').read()

        with tf.Session() as sess:

            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            predictions = sess.run(softmax_tensor,
                                   {'DecodeJpeg/contents:0': image_data})
            predictions = np.squeeze(predictions)
            max_index, max_value = max(enumerate(predictions), lambda p: p[1])
            self.category = Font.CATEGORIES[max_index]

    def extract_slant(self):
        """ Compute slant by getting mean slope of characters """
        meanslant = 0
        # should one use symmetrics or the whole alphabet? Who knows
        # also TODO, when we get linear reps of each letter use that instead
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        for c in list(slstr):
            xp = []
            yp = []
            img = f2i.single_pil(c, self.pilfont)[0]
            px = img.load()
            for y in range(img.size[1]):
                pt = 0
                n = 0
                for x in range(img.size[0]):
                    if px[x, y] == 0:
                        pt += x
                        n += 1
                if n != 0:
                    # THIS IS INTENTIONAL, DON'T CHANGE IT
                    # We want to get the slant off of the normal so we reverse x
                    # and y
                    xp.append(y)
                    yp.append(pt / n)
            slant, offset = np.polyfit(xp, yp, 1)
            meanslant += slant
        self.slant = -meanslant / len(slstr)

    def set_size(self, size):
        self.size = size
        self.pilfont = ImageFont.truetype(self.path, self.size)

    def save(self):
        """ pickles to the cache directory and returns the name of the file """
        pil = self.pilfont
        self.pilfont = None
        pickle.dump(self, open(config.CACHE_LOCATION + "/" +
                               str(self.name) + ".pickle", "wb"))
        self.pilfont = pil
        return self.name.replace(" ", "_")

    def __getstate__(self):
        return self.__dict__

    def __setstate__(self, d):
        self.__dict__ = d
        self.open_path()

    def __str__(self):
        return "Font {} at path {}".format(self.name, self.path)

    @staticmethod
    def extract_name(d):
        """ Extracts just the name from a font to check if it's loaded """
        pilfont = ImageFont.truetype(d)
        family = pilfont.font.family
        style = pilfont.font.style
        return "{} {}".format(family, style)

    @staticmethod
    def scale(feature, value):
        """ Scales a value to its standard dev. across the font set. """
        xprime = (value - Font.scale_values[feature][_MEAN]) / Font.scale_values[feature][_STDDEV]
        x2prime = (((xprime - Font.scale_values[feature][_MIN]) /
                    (Font.scale_values[feature][_MAX] -
                     Font.scale_values[feature][_MIN])) * 10) - 5
        return x2prime

    @staticmethod
    def scale_features():
        """
        Calculates the stddev, mean, min, and max of each feature.
        """
        for f, v in Font.compare.items():
            population = []
            for k in Font.fonts.keys():
                population.append(Font.fonts[k].__dict__[f])
            mean = np.mean(population)
            stddev = np.std(population)
            for idx, p in enumerate(population):
                population[idx] = (p - mean) / stddev
            maximum = max(population)
            minimum = min(population)
            Font.scale_values[f] = (mean, stddev, maximum, minimum)
