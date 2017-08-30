"""
The Font class extracts and stores image data from font files.
It is constructed with a path to a .ttf or .otf file and automatically extracts
visual features.
It also stores some static information on font sorting and categorization.
It also automatically scales font features to uniform values for easier sorting.
"""
from math import sqrt
import pickle
from io import StringIO
import numpy as np
from pkg_resources import resource_string
from PIL import ImageFont, ImageStat
import tensorflow as tf
import typecat.config as config
import typecat.font2img as f2i

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

            self.pilfont = None
            self.extract_pil()
            self.extract_width()
            self.extract_thickness()
            self.extract_category()
            self.extract_slant()

            print("Loaded {} from {}".format(self.name, self.path))

    def open_path(self):
        """ Sets pilfont to the font at self.path """
        self.pilfont = ImageFont.truetype(self.path, size=self.size)
        # check if the font renders properly
        a_render = f2i.single_pil("A", self.pilfont, fore=1, back=0)[0]
        b_render = f2i.single_pil("B", self.pilfont, fore=1, back=0)[0]
        if a_render == b_render:
            print("Could not render {} properly.".format(self.name))
            raise RenderError("Could not render {} properly.".format(self.name))

    def extract_pil(self):
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
        for char in list(fullabc):
            img = f2i.single_pil(char, self.pilfont, fore=1, back=0)[0]
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
        self.thickness = ImageStat.Stat(img).mean


    def getsize(self, *args):
        """ returns the pilfont size """
        return self.pilfont.getsize(*args)

    def extract_category(self):
        """ Uses retrained nn to sort font """
        # FIXME redo with tfdeploy
        img = self.training_img()
        temp_file = StringIO()
        img.save(temp_file, 'JPEG')
        image_data = tf.gfile.FastGFile(temp_file, 'rb').read()

        with tf.Session() as sess:

            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            predictions = sess.run(softmax_tensor,
                                   {'DecodeJpeg/contents:0': image_data})
            predictions = np.squeeze(predictions)
            max_index = max(enumerate(predictions), lambda p: p[1])[0]
            self.category = Font.CATEGORIES[max_index]

    def extract_slant(self):
        """ Compute slant by getting mean slope of characters """
        meanslant = 0
        # should one use symmetrics or the whole alphabet? Who knows
        # also TODO, when we get linear reps of each letter use that instead
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        for char in list(slstr):
            x_pixels = []
            y_pixels = []
            img = f2i.single_pil(char, self.pilfont)[0]
            img_pixels = img.load()
            for y_value in range(img.size[1]):
                x_sum = 0
                total = 0
                for x_value in range(img.size[0]):
                    if img_pixels[x_value, y_value] == 0:
                        x_sum += x_value
                        total += 1
                if total != 0:
                    # THIS IS INTENTIONAL, DON'T CHANGE IT
                    # We want to get the slant off of the normal so we reverse x
                    # and y
                    x_pixels.append(y_value)
                    y_pixels.append(x_sum / total)
            slant = np.polyfit(x_pixels, y_pixels, 1)[0]
            meanslant += slant
        self.slant = -meanslant / len(slstr)

    def set_size(self, size):
        """ Sets the size value of this font and reloads the truetype font at the correct size """
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

    def __setstate__(self, dict_):
        self.__dict__ = dict_
        self.open_path()

    def __str__(self):
        return "Font {} at path {}".format(self.name, self.path)

    @staticmethod
    def extract_name(path):
        """ Extracts just the name from a font to check if it's loaded """
        pilfont = ImageFont.truetype(path)
        family = pilfont.font.family
        style = pilfont.font.style
        return "{} {}".format(family, style)

    @staticmethod
    def scale(feature, value):
        """ Scales a value to its standard dev. across the font set. """
        xprime = (value - Font.scale_values[feature]["mean"]) / Font.scale_values[feature]["stddev"]
        x2prime = (((xprime - Font.scale_values[feature]["min"]) /
                    (Font.scale_values[feature]["max"] -
                     Font.scale_values[feature]["min"])) * 10) - 5
        return x2prime

    @staticmethod
    def scale_features():
        """
        Calculates the stddev, mean, min, and max of each feature.
        """
        for feature, value in Font.compare.items():
            population = []
            for item in Font.fonts:
                population.append(item.__dict__[feature])
            mean = np.mean(population)
            stddev = np.std(population)
            for idx, pop in enumerate(population):
                population[idx] = (pop - mean) / stddev
            maximum = max(population)
            minimum = min(population)
            Font.scale_values[feature] = (mean, stddev, maximum, minimum)
