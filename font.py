import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageStat
from configparser import ConfigParser
import config
import font2img
from numpy import polyfit


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
        thickness
        slant
        width
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
            self.extract_width()
            self.extract_thickness()
            self.extract_category()
            self.extract_slant()

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
        fullabc = Font.ALPHABET + Font.ALPHABET.upper()
        for c in list(fullabc):
            totalwidth += self.pilfont.getsize(c)[0]
        mean = totalwidth / len(fullabc)
        self.width = mean

    def extract_thickness(self):
        """
        Calculates thickness by getting average pixels filled in a
        horizontal sliver of the text
        """
        bmpsize = self.pilfont.getsize(Font.ALPHABET.upper())
        statimg = Image.new("1", (bmpsize[0],
                            bmpsize[1] - self.ascent), color=1)
        draw = ImageDraw.Draw(statimg)
        draw.text((0, -self.descent), Font.ALPHABET.upper(),
                  font=self.pilfont, fill=(0))
        stat = ImageStat.Stat(statimg)
        self.thickness = stat.mean

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
        """ Compute slant by getting mean slope of symmetric characters """
        meanslant = 0
        # should one use symmetrics or the whole alphabet? Who knows
        # also TODO, when we get linear reps of each letter use that instead
        slstr = Font.ALPHABET + Font.ALPHABET.upper()
        for c in list(slstr):
            xp = []
            yp = []
            img = font2img.single_pil(c, self.pilfont)[0]
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

    def set_size(self, size):
        self.size = size
        # TODO this is probably really slow and inefficient
        self.pilfont = ImageFont.truetype(self.path, self.size)

    def display(self, master, w=500, h=500):
        user_text = "Handgloves"
        textstr = "{}\n{}\n{}".format(Font.ALPHABET,
                                      Font.ALPHABET.upper(), user_text)
        photo = font2img.multiline_tk(textstr, self.pilfont,
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
