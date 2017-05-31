import tensorflow as tf
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
import typecat.config as config
import typecat.font2img as f2i
import os
import numpy as np
from math import sin, cos, pi, sqrt
import pickle

from pkg_resources import resource_string

#mean stddev min max
MEAN = 0
STDDEV = 1
MIN = 2
MAX = 3

class RenderError(Exception):
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

    FIVE_CLASS_MODEL = resource_string(__name__,  'models/five_class_graph.pb')

    search_str = ""
    search_categories = []
    fonts = dict()
    scale_values = dict()

    graph = None

    @staticmethod
    def setup_graph():
        print("loading graph")
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(Font.FIVE_CLASS_MODEL)
        Font.graph = tf.import_graph_def(graph_def, name='')

    def dist(self):
        total = 0
        if self.category in Font.search_categories:
            total += 1000
        if Font.search_str != "" and Font.search_str.lower() in self.name.lower():
            total += 100
        for f, v in Font.compare.items():
            if v == -1:
                continue
            if type(v) in [float, int]:
                total += (v - Font.scale(f, self.__dict__[f])) ** 2
            else:
                total += 0 if v == self.__dict__[f] else 1
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
        if type(arg1) is str:
            self.path = arg1
            if arg2 is not None:
                self.size = arg2
            else:
                self.size = 50
            self.open_path()

            self.extract_PIL()
            self.extract_centroid_metrics()
            self.extract_width()
            self.extract_thickness()
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

    def training_img(self):
        temp_size = self.size
        self.set_size(60)
        glyphs = ['Laseg', 'dhum', 'Hloiv']
        current_pos = [25, 25]
        spacing = 60
        img = Image.new("L", (226, 226), 0)
        for g in glyphs:
            temp_img = Image.new(mode="L", size=(226, 226), color=0)
            temp_draw = ImageDraw.Draw(temp_img)
            temp_draw.text((0, 0), g, font=self.pilfont, fill=255)
            bbox = temp_img.getbbox()
            if bbox is None:
                self.set_size(temp_size)
                return temp_img
            width = bbox[2] - bbox[0]
            height = bbox[3] - bbox[1]
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
        for c in list(fullabc):
            img, draw = f2i.single_pil(c, self.pilfont, fore=1, back=0)
            bbox = img.getbbox()
            totalwidth += bbox[2] - bbox[0]
            totalheight += bbox[3] - bbox[1]
        self.height = totalheight / len(fullabc)
        self.width = totalwidth / len(fullabc)
        self.ratio = self.height / self.width

    def extract_thickness(self):
        """
        Calculates thickness by taking the median of thicknesses
        """
        num_vals = sum(self.thicknesses)
        sum_thick = 0
        for val, num in enumerate(self.thicknesses):
            sum_thick += val * num
        mean_thickness = sum_thick / max(1, num_vals)
        self.thickness = mean_thickness
        # calculate stddev
        total = 0
        for val, num in enumerate(self.thicknesses):
            term = (val - self.thickness) ** 2
            total += term * num
        stddevsq = total / max(1, num_vals)
        self.thickness_variation = sqrt(stddevsq)

    def getsize(self, *args):
        return self.pilfont.getsize(*args)

    @staticmethod
    def extract_category():
        """ This is static because it's much faster to generate one graph and run a bunch than regenerate for every font """

        if Font.graph is None:
            Font.setup_graph()

        with tf.Session(graph=Font.graph) as sess:
            softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
            for font in Font.fonts.values():
                img = font.training_img()
                # FIXME this won't work if the user doesn't have r/w privs in the cwd
                img.save(open("tmpfile", 'wb'), 'JPEG')
                image_data = tf.gfile.FastGFile("tmpfile", 'rb').read()
                os.remove("tmpfile")
                predictions = sess.run(softmax_tensor,
                                       {'DecodeJpeg/contents:0': image_data})
                predictions = np.squeeze(predictions)
                max_index, max_value = max(enumerate(predictions), key=lambda p: p[1])
                font.category = Font.CATEGORIES[max_index]

    def extract_slant(self):
        """ Compute slant by getting mean slope of characters """
        meanslant = 0
        # should one use symmetrics or the whole alphabet? Who knows
        # also TODO, when we get linear reps of each letter use that instead
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        for c in list(Font.SYMMETRIC):
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

    def _bound(self, loc, size):
        if(loc[0] >= size[0]):
            loc[0] = size[0] - 1
        if(loc[0] <= 0):
            loc[0] = 0
        if(loc[1] >= size[1]):
            loc[1] = size[1] - 1
        if(loc[1] <= 0):
            loc[1] = 0

    def _shortest_line(self, point, imgpx, size):
        x = point[0]
        y = point[1]
        # it's unlikely a segment will be more than half the size of the img
        shortest_len = size[0]/2
        shortest_pts = ((0, 0), (0, 0))
        for d in range(int(pi / Font.DELTA_RAD)):
            rad = d * Font.DELTA_RAD
            # using sin and cosine will ensure we move exactly 1 pixel each
            # step
            step = (cos(rad), sin(rad))
            nstep = (-cos(rad), -sin(rad))
            # upper is the top point of the line
            upper_loc = [x, y]
            # and lower, naturally, is the bottom part
            lower_loc = [x, y]
            curr_len = 0
            while curr_len < shortest_len:
                # go a little bit further along our angle
                if imgpx[int(upper_loc[0]), int(upper_loc[1])] == 0:
                    upper_loc = [upper_loc[0] + step[0],
                                 upper_loc[1] + step[1]]
                if imgpx[int(lower_loc[0]), int(lower_loc[1])] == 0:
                    lower_loc = [lower_loc[0] + nstep[0],
                                 lower_loc[1] + nstep[1]]
                # bound the vars
                self._bound(upper_loc, size)
                self._bound(lower_loc, size)
                # calculate length
                curr_len = sqrt((upper_loc[0] - lower_loc[0])**2 +
                                (upper_loc[1] - lower_loc[1]) ** 2)
                # if both are white and we're less than the shortest length
                # stop and move on
                if((imgpx[int(lower_loc[0]), int(lower_loc[1])] == 1 and
                        imgpx[int(upper_loc[0]),
                              int(upper_loc[1])] == 1)) and\
                        curr_len < shortest_len:
                    shortest_len = curr_len
                    shortest_pts = (tuple(lower_loc), tuple(upper_loc))
        return shortest_len, shortest_pts

    def set_size(self, size):
        self.size = size
        # TODO_ this is probably really slow and inefficient
        # wontfix, afaik pil doesn't support font resizing
        self.pilfont = ImageFont.truetype(self.path, self.size)

    def extract_centroid_metrics(self):
        # The size is 50, it aint gonna get much bigger
        self.thicknesses = [0]*50
        for c in list(Font.ALPHABET + Font.ALPHABET.upper()):
            img, draw = f2i.single_pil(c, self.pilfont)
            dr = img.copy()
            bbox = img.getbbox()
            img2 = ImageOps.expand(img, border=1, fill=1)
            imgpx = img2.load()
            for x in range(bbox[0], bbox[2]):
                for y in range(bbox[1], bbox[3]):
                    if img.getpixel((x, y)) == 1 or imgpx[x, y] == 1:
                        continue
                    shortest_len, shortest_pts = \
                        self._shortest_line((x, y), imgpx, img2.size)
                    self.thicknesses[int(shortest_len)] += 1
                    # Color in center of mass of shortest line
                    com = (int((shortest_pts[0][0]+shortest_pts[1][0])/2),
                           int((shortest_pts[0][1]+shortest_pts[1][1])/2))
                    dr.putpixel(com, 1)
                    ell = ((shortest_pts[0][0]-shortest_len,
                            shortest_pts[0][1]-shortest_len),
                           (shortest_pts[0][0]+shortest_len,
                            shortest_pts[0][1]+shortest_len))
                    draw.ellipse(ell, fill=1)

    def category_str(self, formatstr, categories):
        """ Converts a display category to a string """
        formatargs = []
        if type(categories) is str:
            val = self.__dict__[categories]
            if type(val) is float:
                val = round(val, 3)
            formatargs.append(val)
        elif type(categories) is tuple or type(categories) is list:
            for i in categories:
                val = self.__dict__[i]
                if type(val) is float:
                    val = round(val, 3)
                formatargs.append(val)
        return formatstr.format(*formatargs)

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
        xprime = ((value - Font.scale_values[feature][MIN]) / (Font.scale_values[feature][MAX] - Font.scale_values[feature][MIN])) * 10 - 5
        return xprime

    @staticmethod
    def scale_features():
        """
        Calculates the stddev, mean, min, and max of each feature.
        """
        for f, v in Font.compare.items():
            population = []
            for k in Font.fonts.keys():
                population.append(Font.fonts[k].__dict__[f])
            maximum = max(population)
            minimum = min(population)
            for p in population:
                p = (p - minimum) / (maximum - minimum)
            mean = np.mean(population)
            stddev = np.std(population)
            Font.scale_values[f] = (mean, stddev, max(population), min(population))
