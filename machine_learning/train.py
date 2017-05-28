import tensorflow as tf
import machine_learning.model as mdl
import machine_learning.font2tensor as f2t
from machine_learning.labels import font_labels
import os

TRAINING_FONT_DIR = '/home/timothy/dl_fonts'

SAVE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/training_data/'

NUM_STEPS = 2000

LEARNING_RATE = .001

model_to_train = mdl.model

META_FILE = 'model.ckpt-60.meta'

with model_to_train.as_default():
    tf.summary.scalar('loss', mdl.loss)

    optimizer = tf.train.GradientDescentOptimizer(LEARNING_RATE)

    global_step = tf.Variable(0, name='global_step', trainable=False)
    train_op = optimizer.minimize(mdl.loss, global_step=global_step)

    with tf.Session() as sess:
        # saver = tf.train.import_meta_graph(SAVE_DIR + META_FILE)
        # saver.restore(sess, tf.train.latest_checkpoint(SAVE_DIR))
        init = tf.global_variables_initializer()
        sess.run(init)
        generator = f2t.generate_batch(mdl.BATCH_SIZE, font_labels, TRAINING_FONT_DIR, True)
        saver = tf.train.Saver(max_to_keep=10)
        for step in range(0, NUM_STEPS):
            images_feed, labels_feed = generator.__next__()
            feed_dict = {
                mdl.fonts_placeholder: sess.run(images_feed),
                mdl.labels_placeholder: sess.run(labels_feed)
            }
            _, loss_value = sess.run([train_op, mdl.loss], feed_dict=feed_dict)
            print('Step {}, loss {}'.format(step, loss_value))
            if step % 10 == 0:
                saver.save(sess, SAVE_DIR + 'model.ckpt', global_step=step)