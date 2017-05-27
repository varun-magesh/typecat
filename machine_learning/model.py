import tensorflow as tf
import machine_learning.font2tensor as f2t
from machine_learning.labels import font_labels
import math
import os


BATCH_SIZE = 5
IMAGE_SQ = 2304
NUM_LABELS = len(font_labels)

HIDDEN_LAYER1_UNITS = 400
HIDDEN_LAYER2_UNITS = 40

LEARNING_RATE = .001
NUM_STEPS = 2000

SAVE_DIR = os.path.dirname(os.path.realpath(__file__)) + '/training_data/'
print(SAVE_DIR)


with tf.Graph().as_default():
    fonts_placeholder = tf.placeholder(dtype=tf.float32, shape=[BATCH_SIZE, IMAGE_SQ])
    labels_placeholder = tf.placeholder(dtype=tf.float32, shape=[BATCH_SIZE, NUM_LABELS])

    theta1 = tf.Variable(tf.truncated_normal([IMAGE_SQ, HIDDEN_LAYER1_UNITS], stddev=1.0 / math.sqrt(float(IMAGE_SQ))))
    bias1 = tf.Variable(tf.zeros([HIDDEN_LAYER1_UNITS]))

    theta2 = tf.Variable(
        tf.truncated_normal([HIDDEN_LAYER1_UNITS, HIDDEN_LAYER2_UNITS], stddev=1.0 / math.sqrt(float(HIDDEN_LAYER1_UNITS))))
    bias2 = tf.Variable(tf.zeros([HIDDEN_LAYER2_UNITS]))

    theta3 = tf.Variable(
        tf.truncated_normal([HIDDEN_LAYER2_UNITS, NUM_LABELS], stddev=1.0 / math.sqrt(float(HIDDEN_LAYER2_UNITS))))
    bias3 = tf.Variable(tf.zeros([NUM_LABELS]))

    hidden1 = tf.nn.relu(tf.matmul(fonts_placeholder, theta1) + bias1)
    hidden2 = tf.nn.relu(tf.matmul(hidden1, theta2) + bias2)
    logits = tf.matmul(hidden2, theta3) + bias3

    labels_placeholder = tf.to_int64(labels_placeholder)
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels_placeholder, logits=logits)
    loss = tf.reduce_mean(cross_entropy)

    tf.summary.scalar('loss', loss)

    optimizer = tf.train.GradientDescentOptimizer(LEARNING_RATE)

    global_step = tf.Variable(0, name='global_step', trainable=False)
    train_op = optimizer.minimize(loss, global_step=global_step)

    with tf.Session() as sess:
        init = tf.global_variables_initializer()
        sess.run(init)
        generator = f2t.generate_batch(BATCH_SIZE, font_labels)
        # saver = tf.train.Saver(max_to_keep=10)
        # saver.restore(sess, SAVE_DIR)
        for step in range(0, NUM_STEPS):
            images_feed, labels_feed = generator.__next__()
            feed_dict = {
                fonts_placeholder: sess.run(images_feed),
                labels_placeholder: sess.run(labels_feed)
            }
            _, loss_value = sess.run([train_op, loss], feed_dict=feed_dict)
            print('Step {}, loss {}'.format(step, loss_value))
            # if step % 5 == 0:
                # saver.save(sess, SAVE_DIR, global_step=step)



