import PIL
import tensorflow as tf
import config
import os
import random
from PIL import Image, ImageDraw, ImageOps
import font

labels = {
    "sans": 1,
    "serif": 2,
    "mono": 3,
    "script": 4,
}

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

def generate_batch(batch_size, labels):
    fontdir = '/home/timothy/dl_fonts'
    font_training_paths = {}
    for dirpath, dirnames, filenames in os.walk(fontdir):
        for d in filenames:
            idx = d.rfind(".")
            if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                font_training_paths[(os.path.join(dirpath, d))] = labels[dirpath.split("/")[-1]]
    while True:
        choice_list = []
        images = tf.placeholder(dtype=tf.float32, shape=[None, 2304])
        labels = tf.placeholder(dtype=tf.float32, shape=[None, len(labels)])
        for i in range(0, batch_size):
            choice = random.choice(list(font_training_paths.keys()))
            choice_label = font_training_paths[choice]
            tf.concat(values=[images, font2tensor(font.Font(choice).set_size(36))], axis=0)
            tf.concat(values=[labels, tf.one_hot(depth=len(labels), indices=choice_label)], axis=0)
        yield images, labels


generator = generate_batch(5, labels)

print(generator.__next__())


