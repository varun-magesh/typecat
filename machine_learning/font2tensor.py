import PIL
import tensorflow as tf
import typecat.config as config
import os
import random
from PIL import Image, ImageDraw, ImageOps
import typecat.font as font
from machine_learning.labels import font_labels

def font2tensor(font):
    font.set_size(36)
    img = fingerprint(font.pilfont)
    return tf.expand_dims(tf.convert_to_tensor(list(img.getdata()), dtype=tf.float32), 0)


def fingerprint(pilfont):
    glyph = 'l'
    temp_img = Image.new("L", (48, 48), 255)
    temp_draw = ImageDraw.Draw(temp_img)
    temp_draw.text((0, 0), glyph, fill=0, font=pilfont)
    temp_img = ImageOps.invert(temp_img)
    bbox = temp_img.getbbox()
    if bbox is None:
        return temp_img
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    temp_crop = temp_img.crop(bbox)
    print(width, height)
    img = Image.new("L", (48, 48), 0)
    img.paste(temp_crop, (int(img.size[0]/2.0 - width/2.0), int(img.size[1]/2.0 - height/2.0)))
    # img.show()
    return img


def generate_batch(batch_size, labels, fontdir, do_labels):
    font_training_paths = {}
    for dirpath, dirnames, filenames in os.walk(fontdir):
        for d in filenames:
            idx = d.rfind(".")
            if idx != -1 and d[idx:] in config.FONT_FILE_EXTENSIONS:
                if do_labels:
                    font_training_paths[(os.path.join(dirpath, d))] = labels[dirpath.split("/")[-1]]
                else:
                    font_training_paths[(os.path.join(dirpath, d))] = 'none'
    global_counter = 0
    while True:

        images = tf.zeros(shape=[0, 2304], dtype=tf.float32)
        image_labels = tf.zeros(dtype=tf.float32, shape=[0, len(labels)])
        counter = 0
        while counter < batch_size:
            choice = list(font_training_paths.keys())[global_counter]
            global_counter += 1
            if global_counter == len(list(font_training_paths.keys())):
                global_counter = 0
            try:
                choice_font = font.Font(choice, 36)
            except Exception:
                continue
            if choice_font is None:
                continue
            images = tf.concat(values=[images, font2tensor(choice_font)], axis=0)
            if do_labels:
                choice_label = font_training_paths[choice]

                image_labels = tf.concat(values=[image_labels, tf.expand_dims(tf.one_hot(depth=len(labels), indices=choice_label - 1), 0)], axis=0)
            counter+=1

        if do_labels:
            yield images, image_labels
        else:
            yield images