import tkinter as tk
from PIL import Image, ImageDraw, ImageFont, ImageTk
from configparser import ConfigParser
import config


class Font(object):
    """
    Stores cached information about fonts in memory.
    Attributes:
        name
        path
        category: serif, sans, display, etc.
        languages
        thickness
        slant = 0
        width = 0
        style: bold, thin, italic etc.
        ascender: space between lowercase height and uppercase height
        descender: length of tail on 'p', 'q', and others
        features: str of special characters supported
        TODO curve quantification
    """
    def __init__(self, name, cp):
        if type(cp) is ConfigParser:
            # load from config
            raise NotImplementedError("Font cannot yet load from config.")
            return
        self.name = name
        self.path = cp

    def display(self, master, w=500, h=500):
        # draw preview
        image = Image.new("RGB", (w - 10, 100), config.PIL_BACKGROUND)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.path, 20)
        alphabet = "abcdefghijklmnopqrstuvwxyz"
        draw.text((10, 25), alphabet, font=font, fill=(0, 0, 0))
        draw.text((10, 55), alphabet.upper(), font=font, fill=(0, 0, 0))

        photo = ImageTk.PhotoImage(image)

        font = tk.Frame()
        font.configure(background=config.BACKGROUND)

        # draw title
        title = tk.Label(font, text=self.name,
                         font=config.HEADING_FONT,
                         padx=10,
                         pady=10,
                         background=config.BACKGROUND,
                         foreground=config.HEADING_COLOR)
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
