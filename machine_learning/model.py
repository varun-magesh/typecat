import tensorflow as tf
from machine_learning.labels import font_labels
import math

BATCH_SIZE = 20
IMAGE_SQ = 2304
NUM_LABELS = len(font_labels)

HIDDEN_LAYER1_UNITS = 1000
HIDDEN_LAYER2_UNITS = 1000
HIDDEN_LAYER3_UNITS = 50

model = tf.Graph()

with model.as_default():
    fonts_placeholder = tf.placeholder(dtype=tf.float32, shape = [BATCH_SIZE, IMAGE_SQ])
    labels_placeholder = tf.placeholder(dtype=tf.float32, shape = [BATCH_SIZE, NUM_LABELS])

    theta1 = tf.Variable(tf.truncated_normal([IMAGE_SQ, HIDDEN_LAYER1_UNITS], stddev=1.0 / math.sqrt(float(IMAGE_SQ))))
    bias1 = tf.Variable(tf.zeros([HIDDEN_LAYER1_UNITS]))

    theta2 = tf.Variable(
        tf.truncated_normal([HIDDEN_LAYER1_UNITS, HIDDEN_LAYER2_UNITS],
                            stddev=1.0 / math.sqrt(float(HIDDEN_LAYER1_UNITS))))
    bias2 = tf.Variable(tf.zeros([HIDDEN_LAYER2_UNITS]))

    theta3 = tf.Variable(
        tf.truncated_normal([HIDDEN_LAYER2_UNITS, HIDDEN_LAYER3_UNITS],
                            stddev=1.0 / math.sqrt(float(HIDDEN_LAYER2_UNITS))))
    bias3 = tf.Variable(tf.zeros([HIDDEN_LAYER3_UNITS]))

    theta4 = tf.Variable(
        tf.truncated_normal([HIDDEN_LAYER3_UNITS, NUM_LABELS], stddev=1.0 / math.sqrt(float(HIDDEN_LAYER3_UNITS))))
    bias4 = tf.Variable(tf.zeros([NUM_LABELS]))

    hidden1 = tf.nn.relu(tf.matmul(fonts_placeholder, theta1) + bias1)
    hidden2 = tf.nn.relu(tf.matmul(hidden1, theta2) + bias2)
    hidden3 = tf.nn.relu(tf.matmul(hidden2, theta3) + bias3)
    logits = tf.matmul(hidden3, theta4) + bias4

    labels_placeholder = tf.to_int64(labels_placeholder)
    cross_entropy = tf.nn.softmax_cross_entropy_with_logits(labels=labels_placeholder, logits=logits)
    loss = tf.reduce_mean(cross_entropy)
