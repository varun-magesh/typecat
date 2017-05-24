import PIL
import tensorflow as tf
from font import Font
import font2img

from PIL import Image, ImageDraw, ImageOps


def font2tensor(font):
    font.set_size(36)
    img = fingerprint(font.pilfont)
    img = PIL.ImageOps.invert(img)
    return tf.convert_to_tensor(list(img.getdata()), dtype=tf.float32)



def fingerprint(pilfont):

    glyphs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    img = Image.new("RGBA", (48, 48), (255, 255, 255, 255))

    for g in glyphs:
        temp_img = Image.new("RGBA", (48, 48), (255, 255, 255, 0))
        glyph = ImageDraw.Draw(temp_img)
        posx = img.size[0] / 2 - pilfont.getsize(g)[0]/2
        posy = 0
        glyph.text((posx, posy), g, fill=(0, 0, 0, 10), font=pilfont)
        img = Image.alpha_composite(img, temp_img)

    return img.convert('L')

print(font2tensor(Font("/usr/share/fonts/truetype/freefont/FreeSansBold.ttf")))




