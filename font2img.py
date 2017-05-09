import PIL
from PIL import Image, ImageDraw, ImageTk
import config


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


def single_pil(text, pilfont, size=None, mode="1", fore=0, back=1):
    """ Creates a one row b&w image of text to quantify """
    bmpsize = (0, 0)
    bmpsize = pilfont.getsize(text) if size is None else size
    img = Image.new(mode, bmpsize, color=1)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=pilfont, fill=(0))
    return (img, draw)
