from PIL import Image, ImageDraw, ImageTk, ImageFont
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

path = sys.argv[1]
if path[-1] != "/":
        path += "/"
for f in os.listdir(path):
        if ".ttf" in f or ".otf" in f:
                print(path+f)
                font = ImageFont.load(path+f)
                img = multiline("abcdefghijklmnopABCDEFGHIJKLMNOP\nHandgloves\nRen", font, (500, 500))
                img.save(path+f+".jpg", "JPEG")
 
             
