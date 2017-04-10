import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageStat, ImageOps
import config
import font2img as f2i
from numpy import polyfit
from math import sin, cos, pi, sqrt
import pickle


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

    DELTA_RAD = pi/18
    DISPLAY_CATEGORIES = [
        ('Category: {}', 'category'),
        ('Width: {} Height: {} Ratio: {}',
         ('width', 'height', 'ratio')),
        ('Slant: {}', 'slant'),
        ('Thickness: {}', 'thickness'),
        ('Thickness Variation: {}', 'thickness_variation'),
        ('Path: {}', 'path')
    ]

    def __init__(self, arg1, arg2=None):
        # option 1: a path to a font to go find the details yourself
        if type(arg1) is str and arg2 is None:
            self.path = arg1
            self.size = 50
            self.open_path()

            self.extract_PIL()
            self.extract_centroid_metrics()
            self.extract_width()
            self.extract_thickness()
            self.extract_category()
            self.extract_slant()

            print("Loaded {} from {}".format(self.name, self.path))

    def open_path(self):
        self.pilfont = ImageFont.truetype(self.path, size=self.size)

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
        mean_thickness = sum_thick / max(1, num_vals)
        self.thickness = mean_thickness
        # calculate stddev
        total = 0
        for val, num in enumerate(self.thicknesses):
            term = (val - self.thickness) ** 2
            total += term * num
        stddevsq = total / max(1, num_vals)
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

    def display(self, w=500, h=500, master=None):
        """
        Returns a tk.Frame of information about the font that
            scales to the size required, in theory.
        """
        # option one: an actual full display with everything on it
        if h > 300 and w > 300:
            return self.info_panel(w, h, master)
        else:
            return self.name_panel(w, h, master)

    def name_panel(self, w=500, h=500, master=None):
        # TODO buttons are really jerky and dont' work when you click text or
        # image, only the side
        button = 0
        if master is None:
            button = tk.Button(borderwidth=1, relief=tk.RAISED, width=w)
        else:
            button = tk.Button(master, borderwidth=1, relief=tk.RAISED, width=w)
        # button.grid_propagate(0)
        frame = tk.Label(button)
        hpad = int(h/100)
        wpad = int(w/100)
        size = int(h/1.5)
        self.set_size(size)
        text = "xgcZa"
        photo = f2i.multiline_tk(text, self.pilfont,
                                 (int(w/4), int(h+2*hpad)),
                                 padx=wpad, pady=hpad)
        label = tk.Label(relief=tk.SOLID, borderwidth=1)
        label.image = photo
        label.configure(image=photo)
        label.grid(padx=wpad, pady=hpad, row=0, column=0,
                   sticky=tk.W, in_=frame, columnspan=1)

        title = tk.Label(frame, text=self.name,
                         font=config.body_font(size),
                         padx=wpad, pady=hpad)
        title.grid(sticky=tk.E, in_=frame, columnspan=2, column=1, row=0)
        frame.grid(in_=button)
        return button

    def info_panel(self, w=500, h=500, master=None):
            font = 0
            if master is None:
                font = tk.Frame(borderwidth=1, relief=tk.SOLID,
                                width=w, height=h)
            else:
                font = tk.Frame(master, borderwidth=1, relief=tk.SOLID,
                                width=w, height=h)
            hpad = int(h / 100)
            wpad = int(w / 100)

            # draw title
            titlesize = int(w/len(self.name))
            title = tk.Label(font, text=self.name,
                             font=config.heading_font(titlesize),
                             padx=wpad, pady=hpad)
            title.grid(sticky=tk.N, in_=font, columnspan=2)

            # display preview
            label = tk.Label(relief=tk.SOLID, borderwidth=1)

            # TODO varying colors and randomly chosen phrases
            user_text = "Handgloves"

            # callback to set text and text size
            def set_text(text, size=self.size):
                # TODO not good practice
                if size != self.size and (type(size) == int or size.isdigit()):
                    size = int(size)
                    # Things get nasty if you punch in a number too big
                    if(size > 200):
                        size = 200
                    self.set_size(size)
                # TODO automatically set font size to a reasonable level when
                # started
                # FIXME if you change the size and then the text it sometimes
                # won't change until you change the text again
                photo = f2i.multiline_tk(text, self.pilfont,
                                         (int(w), int(h/2)),
                                         padx=wpad, pady=hpad)
                label.image = photo
                label.configure(image=photo)
                label.grid(padx=wpad, pady=hpad, row=1, column=0,
                           sticky=tk.N, in_=font, columnspan=2)

            set_text(user_text)

            font.grid_columnconfigure(1, minsize=int(w/75))
            font.grid_columnconfigure(0, weight=1)

            # text entry
            svtext = tk.StringVar()
            svtext.trace("w", lambda n, idx, mode,
                         sv=svtext: set_text(svtext.get()))
            textin = tk.Entry(font, textvariable=svtext)
            textin.delete(0, tk.END)
            textin.insert(0, "Handgloves")
            textin.grid(sticky=tk.W+tk.E, padx=wpad, pady=hpad, in_=font,
                        row=2, column=0)

            # font size entry
            sv1 = tk.StringVar()
            sv1.trace("w", lambda n, idx, mode, sv=sv1:
                      set_text(svtext.get(), sv.get()))
            sizein = tk.Entry(font, textvariable=sv1, width=3)
            sizein.delete(0, tk.END)
            sizein.insert(0, str(self.size))
            sizein.grid(sticky=tk.E, padx=wpad, pady=hpad,
                        in_=font, row=2, column=1)

            # attributes with a scrollbar
            scrollbar = tk.Scrollbar(font)
            scrollbar.grid(sticky=tk.W+tk.N+tk.S, row=3, column=1,
                           padx=wpad, pady=hpad)
            listbox = tk.Listbox(font)
            listbox.grid(sticky=tk.E+tk.W, padx=wpad, pady=hpad,
                         row=3, column=0)
            for i in Font.DISPLAY_CATEGORIES:
                listbox.insert(tk.END, self.category_str(i[0], i[1]))
            listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=listbox.yview)

            return font

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

    @staticmethod
    def extract_name(d):
        """ Extracts just the name from a font to check if it's loaded """
        pilfont = ImageFont.truetype(d)
        family = pilfont.font.family
        style = pilfont.font.style
        return "{} {}".format(family, style)
