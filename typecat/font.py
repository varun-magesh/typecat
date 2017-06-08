"""
Contains the Font class and the RenderError thrown when a font cannot be rendered correctly.
"""
import os
from math import pi, sqrt
import pickle
import numpy as np
import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
import typecat.config as config
import typecat.font2img as f2i

from pkg_resources import resource_string

#mean stddev min max
MEAN = 0
STDDEV = 1
MIN = 2
MAX = 3

class RenderError(Exception):
    """ Thrown when a font cannot be rendered correctly and is displayed as boxes. """
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
        display_categories: list of strings and values to display,
                            first idx in tuple is name and second is dict value
        ratio: height/width
        style: bold, thin, italic etc.
        ascent: space between lowercase height and uppercase height
        descent: length of tail on 'p', 'q', and others
        features: str of special characters supported
        TODO curve quantification
    """

    ALPHABET = "abcdefghijklmnopqrstuvwxyz"
    SYMMETRIC = "HITl"
    MONOSPACE = "Monospace"
    SERIF = "Serif"
    SANS = "Sans Serif"
    DISPLAY = "Display"
    HANDWRITING = "Handwriting"
    BLOCK = "Block"

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

    DELTA_RAD = pi/18
    compare = {
        "slant": -1,
        "thickness": -1,
        "width": -1,
        "height": -1,
        "ascent": -1,
        "descent": -1,
    }

    FIVE_CLASS_MODEL = resource_string(__name__, 'models/five_class_graph.pb')

    search_str = ""
    search_categories = []
    fonts = dict()
    scale_values = dict()

    graph = None

    @staticmethod
    def setup_graph():
        """ Loads the tensorflow graph from the trained .pb file """
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(Font.FIVE_CLASS_MODEL)
        Font.graph = tf.import_graph_def(graph_def, name='')

    def __init__(self, arg1, arg2=None):
        # option 1: a path to a font to go find the details yourself
        if isinstance(arg1, str):
            self.path = arg1
            if arg2 is not None:
                self.size = arg2
            else:
                self.size = 50

            # We don't find category until the end of loading but some functions just do some
            # preliminary stuff with them before
            self.category = None
            self.pilfont = None

            self.open_path()
            self.extract_pil()
            self.extract_width()
            self.extract_thickness()
            self.extract_slant()

            print("Loaded {} from {}".format(self.name, self.path))

    def open_path(self):
        """ Opens a font from a given system path and checks to see if it renders correctly """
        self.pilfont = ImageFont.truetype(self.path, size=self.size)
        a_img = f2i.single_pil("A", self.pilfont, fore=1, back=0)[0]
        b_img = f2i.single_pil("B", self.pilfont, fore=1, back=0)[0]
        if a_img == b_img:
            print("Could not render {} properly.".format(self.name))
            raise RenderError("Could not render {} properly.".format(self.name))

    def extract_pil(self):
        """ Extracts all data already collected by PIL fonts """
        self.name = "{} {}".format(self.pilfont.font.family, self.pilfont.font.style)
        self.ascent = self.pilfont.font.ascent
        self.descent = self.pilfont.font.descent

    def training_img(self):
        """ Generates an image to pass through the neural net in the style of fontjoy """
        temp_size = self.size
        self.set_size(60)
        glyphs = ['Laseg', 'dhum', 'Hloiv']
        current_pos = [25, 25]
        spacing = 60
        img = Image.new("L", (226, 226), 0)
        for glyph in glyphs:
            temp_img = Image.new(mode="L", size=(226, 226), color=0)
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((0, 0), glyph, font=self.pilfont, fill=255)
            bbox = temp_img.getbbox()
            if bbox is None:
                self.set_size(temp_size)
                return temp_img
            temp_crop = temp_img.crop(bbox)
            img.paste(temp_crop, tuple(current_pos))
            current_pos[1] = current_pos[1] + spacing
        self.set_size(temp_size)
        return ImageOps.invert(img)

    def extract_width(self):
        """ Infers width by averaging individual character widths. """
        totalwidth = 0
        totalheight = 0
        fullabc = Font.ALPHABET + Font.ALPHABET.upper()
        for ch_img in list(fullabc):
            img = f2i.single_pil(ch_img, self.pilfont, fore=1, back=0)[0]
            bbox = img.getbbox()
            totalwidth += bbox[2] - bbox[0]
            totalheight += bbox[3] - bbox[1]
        self.height = totalheight / len(fullabc)
        self.width = totalwidth / len(fullabc)
        self.ratio = self.height / self.width

    def extract_thickness(self):
        """
        Calculates thickness by averaging dark bits
        """
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        img = f2i.single_pil(slstr, self.pilfont)[0]
        self.thickness = ImageStat.Stat(img).mean[0]

    def getsize(self, *args):
        """
        Doesn't get fontsize! wrapper for pilfont.getsize which gets the length it would take to
        render a string
        """
        return self.pilfont.getsize(*args)

    @staticmethod
    def pil2tensor(img):
        img = img.convert("RGB")
        img = np.array(img.resize((299, 299))).reshape(1, 299, 299, 3)
        #return np.expand_dims(np_img, axis=0)
        return img

    @staticmethod
    def extract_category():
        """
        Runs the font file through Inception & the retrained layer to find its category
        This is static because it's much faster to generate one graph and run a bunch than
        regenerate for every font
        """

        if Font.graph is None:
            Font.setup_graph()

        with tf.Session(graph=Font.graph) as sess:
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            for font in Font.fonts.values():
                img = font.training_img()
                predictions = sess.run(softmax_tensor,
                                       {'Mul:0': Font.pil2tensor(img)})
                predictions = np.squeeze(predictions)
                max_index = max(enumerate(predictions), key=lambda p: p[1])[0]
                font.category = Font.CATEGORIES[max_index]

    def extract_slant(self):
        """ Compute slant by getting mean slope of characters """
        meanslant = 0
        # should one use symmetrics or the whole alphabet? Who knows
        # also TODO, when we get linear reps of each letter use that instead
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        for glyph in list(Font.SYMMETRIC):
            x_points = []
            y_points = []
            img = f2i.single_pil(glyph, self.pilfont)[0]
            pixels = img.load()
            for y_val in range(img.size[1]):
                point = 0
                number = 0
                for x_val in range(img.size[0]):
                    if pixels[x_val, y_val] == 0:
                        point += x_val
                        number += 1
                if number != 0:
                    # THIS IS INTENTIONAL, DON'T CHANGE IT
                    # We want to get the slant off of the normal so we reverse x
                    # and y
                    x_points.append(y_val)
                    y_points.append(point/number)
            slant = np.polyfit(x_points, y_points, 1)[0]
            meanslant += slant
        self.slant = -meanslant / len(slstr)

    def set_size(self, size):
        """ set current font size """
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

    def __setstate__(self, dic):
        self.__dict__ = dic
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
        xprime = ((value - Font.scale_values[feature][MIN]) /
                  (Font.scale_values[feature][MAX] - Font.scale_values[feature][MIN])) * 10 - 5
        return xprime

    @staticmethod
    def scale_features():
        """
        Calculates the stddev, mean, min, and max of each feature.
        """
        for feature in Font.compare:
            population = []
            for value in Font.fonts.values():
                population.append(value.__dict__[feature])
            maximum = max(population)
            minimum = min(population)
            mean = np.mean(population)
            #TODO STddev scaling
            stddev = np.std(population)
            Font.scale_values[feature] = (mean, stddev, max(population), min(population))

    def dist(self):
        """
        Finds the Euclidean distance between the features of this font and the desired features
        such as thickness, category, name, etc.
        """
        total = 0
        if self.category in Font.search_categories:
            total += 100
        if Font.search_str != "" and Font.search_str.lower() in self.name.lower():
            total += 100
        for feature, value in Font.compare.items():
            if value == -1:
                continue
            if isinstance(value, (float, int)):
                total += (value - Font.scale(feature, self.__dict__[feature])) ** 2
            else:
                total += 0 if value == self.__dict__[feature] else 1
        return sqrt(total)

    def __lt__(self, other):
        return self.dist() < other.dist()

    def __gt__(self, other):
        return self.dist() > other.dist()

    def __eq__(self, other):
        return self.dist() == other.dist()

    def __ne__(self, other):
        return self.dist() != other.dist()
