from PIL import Image, ImageDraw, ImageFont
import sys
import os

def multiline(text, pilfont, size, mode="RGB",
                 padx=0, pady=0, spacing=0,
                 background=(255,255,255), foreground=(0, 0, 0)):
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
        return image

with open("fontlist") as fl:
    for f in fl.readlines():
        try:
            f = f.strip()
            f = f[:f.find(":")].strip()
            font = ImageFont.truetype(f, size=75)
            img = multiline("abcdefghijklmnopABCDEFGHIJKLMNOP\nHandgloves\nRen", font, (500, 500))
            img.save("imgs/"+f[f.rfind("/"):-4]+".jpg", "JPEG")
        except Exception:
            pass #FIXME what the f

