import PIL
import tensorflow as tf
import config
import os
import random
from PIL import Image, ImageDraw, ImageOps
import font

def font2tensor(font):
    font.set_size(36)
    img = fingerprint(font.pilfont)
    img = PIL.ImageOps.invert(img)
    return tf.expand_dims(tf.convert_to_tensor(list(img.getdata()), dtype=tf.float32), 0)


def fingerprint(pilfont):
    glyphs = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    img = Image.new("RGBA", (48, 48), (255, 255, 255, 255))

    for g in glyphs:
        temp_img = Image.new("RGBA", (48, 48), (255, 255, 255, 0))
        glyph = ImageDraw.Draw(temp_img)
        posx = img.size[0] / 2 - pilfont.getsize(g)[0] / 2
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
        images = tf.zeros(shape=[0, 2304], dtype=tf.float32)
        image_labels = tf.zeros(dtype=tf.float32, shape=[0, len(labels)])
        counter = 0
        while counter < batch_size:
            choice = random.choice(list(font_training_paths.keys()))
            try:
                choice_font = font.Font(choice, 36)
            except Exception:
                continue
            if choice_font is None:
                continue
            choice_label = font_training_paths[choice]
            images = tf.concat(values=[images, font2tensor(choice_font)], axis=0)
            image_labels = tf.concat(
                values=[image_labels, tf.expand_dims(tf.one_hot(depth=len(labels), indices=choice_label - 1), 0)],
                axis=0)
            counter+=1
        yield images, image_labels
