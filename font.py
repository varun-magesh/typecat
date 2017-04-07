import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
from configparser import ConfigParser
import config
import font2img as f2i
from numpy import polyfit
from math import sin, cos, pi, sqrt


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
        mean_thickness: average thickness
        thickness_variation: standard dev. of thicknesses
        slant
        width
        height
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

    DELTA_RAD = pi/18

    def __init__(self, arg1, arg2=None):
        # option 1: a font name and a config file to load in from
        if type(arg1) is str and type(arg2) is ConfigParser:
            # load from config
            self.name = arg1
            raise NotImplementedError("Font cannot yet load from config.")
        # option 2: a path to a font to go find the details yourself
        elif type(arg1) is str and arg2 is None:
            self.path = arg1
            self.size = 50
            self.pilfont = ImageFont.truetype(self.path, size=self.size)

            self.extract_PIL()
            self.extract_centroid_metrics()
            self.extract_width()
            self.extract_thickness()
            self.extract_category()
            self.extract_slant()
            print("{} {}".format(self.name, self.thickness_variation))

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
        self.ratio = self.height / self.width

    def extract_thickness(self):
        """
        Calculates thickness by taking the median of thicknesses
        """
        num_vals = sum(self.thicknesses)
        sum_thick = 0
        for val, num in enumerate(self.thicknesses):
            sum_thick += val * num
        mean_thickness = sum_thick / num_vals
        self.thickness = mean_thickness
        # calculate stddev
        total = 0
        for val, num in enumerate(self.thicknesses):
            term = (val - self.thickness) ** 2
            total += term * num
        stddevsq = total / num_vals
        self.thickness_variation = sqrt(stddevsq)

    def extract_category(self):
        # Check if serif by using the uppercase T
        # Should be unique to serif characters, might also pick up
        # calligraphy?
        linestr = "T"
        bmpsize = self.pilfont.getsize(linestr)

        lineimg = Image.new("1", bmpsize, color=1)

        mask = Image.new("1", bmpsize, color=1)
        drawmask = ImageDraw.Draw(mask)

        draw = ImageDraw.Draw(lineimg)
        draw.text((0, 0), linestr, font=self.pilfont, fill=(0))

        widths = set()
        for y in range(int(2 * bmpsize[1] / 3), bmpsize[1]):
            drawmask.rectangle([(0, 0), bmpsize], fill=0)
            drawmask.line([(0, y), (bmpsize[0], y)], fill=1)
            stat = ImageStat.Stat(lineimg, mask)
            widths.add(stat.sum[0])
        # TODO there are more categories than just serif and sans
        if(len(widths) != 1):
            self.category = Font.SERIF
        else:
            self.category = Font.SANS

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
            slant, offset = polyfit(xp, yp, 1)
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
        # TODO this is probably really slow and inefficient
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

    def display(self, master=None, w=500, h=500):
        user_text = "Handgloves"
        textstr = "{}\n{}\n{}".format(Font.ALPHABET,
                                      Font.ALPHABET.upper(), user_text)
        photo = f2i.multiline_tk(textstr, self.pilfont,
                                 (w-10, h), padx=10, pady=10)

        font = tk.Frame()
        font.configure()

        # draw title
        title = tk.Label(font, text=self.name,
                         font=config.HEADING_FONT,
                         padx=10,
                         pady=10)
        title.grid()

        # display preview
        label = tk.Label(font, image=photo)
        label.image = photo
        label.grid(padx=10, pady=10)

        # text entry
        e = tk.Entry(font)
        e.delete(0, tk.END)
        e.insert(0, "20")
        e.grid(sticky=tk.E+tk.W, padx=10, pady=10)

        font.pack()
        return font
