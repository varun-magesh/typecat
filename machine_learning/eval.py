import tensorflow as tf
import machine_learning.model as mdl
import machine_learning.font2tensor as f2t
from machine_learning.labels import font_labels
import os

EVAL_FONT_DIR = '/home/timothy/dl_fonts'

SAVE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/training_data/'
META_FILE = 'model.ckpt-480.meta'

NUM_TO_EVAL = mdl.BATCH_SIZE

model_to_eval = mdl.model

with model_to_eval.as_default():

    with tf.Session() as sess:
        saver = tf.train.import_meta_graph(SAVE_DIR + META_FILE)

        saver.restore(sess, tf.train.latest_checkpoint(SAVE_DIR))
        init = tf.global_variables_initializer()
        sess.run(init)
        generator = f2t.generate_batch(NUM_TO_EVAL, font_labels, EVAL_FONT_DIR, True)
        predictions = tf.equal(tf.argmax(mdl.logits, 1), tf.argmax(mdl.labels_placeholder, 1))
        accuracy = tf.reduce_mean(tf.cast(predictions, tf.float32))
        images_feed, labels_feed = generator.__next__()
        feed_dict = {
            mdl.fonts_placeholder: sess.run(images_feed),
            mdl.labels_placeholder: sess.run(labels_feed)
        }
        print(sess.run(accuracy, feed_dict=feed_dict))