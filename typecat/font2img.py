from PIL import Image, ImageDraw, ImageTk
import typecat.config as config
import gi
gi.require_version('Gtk', '3.0')
import array
from gi.repository import Gtk, Gdk, GLib, GdkPixbuf

def multiline_tk(text, pilfont, size, mode="RGB",
                 padx=0, pady=0, spacing=0,
                 background=config.PIL_BACKGROUND, foreground=(0, 0, 0)):
        """ Automatically spaces and fits text to an image """
        image = Image.new(mode, size, background)
        draw = ImageDraw.Draw(image)

        totalwidth = size[0] - padx * 2
        textlist = list(text)
        # add a newline whenever we run out of room
        s = 0
        e = 0
        while e < len(textlist):
            substr = "".join(textlist[s:e])
            if textlist[e] == '\n':
                s = e + 1
                e = e + 2
            elif pilfont.getsize(substr)[0] > totalwidth:
                textlist.insert(e - 1, '\n')
                s = e
                e += 1
            else:
                e += 1

        draw.multiline_text((padx, pady), "".join(textlist), font=pilfont,
                            fill=foreground, spacing=spacing)

        photo = ImageTk.PhotoImage(image)
        return photo


def multiline_gtk(text, pilfont, size, mode="RGB", padx=0, pady=0, spacing=0,
                  background=config.PIL_BACKGROUND, foreground=(0, 0, 0)):
        """ Automatically spaces and fits text to an image """
        image = Image.new(mode, size, background)
        draw = ImageDraw.Draw(image)

        totalwidth = size[0] - padx * 2
        textlist = list(text)
        # add a newline whenever we run out of room
        s = 0
        e = 0
        while e < len(textlist):
            substr = "".join(textlist[s:e])
            if textlist[e] == '\n':
                s = e + 1
                e = e + 2
            elif pilfont.getsize(substr)[0] > totalwidth:
                textlist.insert(e - 1, '\n')
                s = e
                e += 1
            else:
                e += 1

        draw.multiline_text((padx, pady), "".join(textlist), font=pilfont,
                            fill=foreground, spacing=spacing)

        return pil2gtk(image)

def pil2gtk(im):
    """Convert Pillow image to GdkPixbuf"""
    data = im.tobytes()
    w, h = im.size
    data = GLib.Bytes.new(data)
    pix = GdkPixbuf.Pixbuf.new_from_bytes(data, 0,
            False, 8, w, h, w * 3)
    return pix
"""
def pil2gtk(im):
    arr = array.array('B', im.tobytes())
    width, height = im.size
    return GdkPixbuf.Pixbuf.new_from_data(arr, GdkPixbuf.Colorspace.RGB,
                                          True, 8, width, height, width * 4)
"""


def single_pil(text, pilfont, size=None, mode="1", fore=0, back=1):
    """ Creates a one row b&w image of text to quantify """
    bmpsize = (0, 0)
    bmpsize = pilfont.getsize(text) if size is None else size
    img = Image.new(mode, bmpsize, color=1)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=pilfont, fill=(0))
    return (img, draw)

def fingerprint(pilfont):
    glyphs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    maxSize = pilfont.getsize('a')
    for g in glyphs:
        if  pilfont.getsize(g) > maxSize:
            maxSize = pilfont.getsize(g)
    img = Image.new("RGBA", maxSize, (255, 255, 255, 255))

    for g in glyphs:
        temp_img = Image.new("RGBA", maxSize, (255, 255, 255, 0))
        glyph = ImageDraw.Draw(temp_img)
        posx = img.size[0] / 2 - pilfont.getsize(g)[0]/2
        posy = 0#img.size[1] / 2 - pilfont.getsize(g)[1]/2
        gpos = (posx, posy)
        glyph.text(gpos, g, fill=(0, 0, 0, 10), font=pilfont)
        img = Image.alpha_composite(img, temp_img)
    img = ImageTk.PhotoImage(img)
    return img

