import numpy as np
import tensorflow as tf
import os.path
from StringIO import StringIO

FIVE_CLASS_MODEL = 'model/five_class_graph.pb'
FIVE_CLASS_LABELS = 'model/five_class_labels.txt'

with tf.gfile.FastGFile(modelFullPath, 'rb') as f:
graph_def = tf.GraphDef()
graph_def.ParseFromString(f.read())
_ = tf.import_graph_def(graph_def, name='')


def classify(font):
    answer = None

    image_data = tf.gfile.FastGFile(imagePath, 'rb').read()
    img = font.training_img()
    f = StringIO()
    img.save(f, 'JPEG')
    image_data = tf.gfile.FastGFile(f, 'rb').read()

    with tf.Session() as sess:

        softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')
        predictions = sess.run(softmax_tensor,
                               {'DecodeJpeg/contents:0': image_data})
        predictions = np.squeeze(predictions)

        top_k = predictions.argsort()[-5:][::-1]  # Getting top 5 predictions
        f = open(labelsFullPath, 'rb')
        lines = f.readlines()
        labels = [str(w).replace("\n", "") for w in lines]
        for node_id in top_k:
            human_string = labels[node_id]
            score = predictions[node_id]
            print('%s (score = %.5f)' % (human_string, score))

        answer = labels[top_k[0]]
        return answer
