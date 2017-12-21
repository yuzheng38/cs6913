# -*- coding: utf-8 -*-

import numpy as np
import os
import pandas as pd
import pickle
import shutil
import tensorflow as tf

from sklearn import metrics

REMOVE_OLD_MODEL = False

DATA_SET_FILE = '../data/training_data.csv'
MODEL_DIR = '../model_dir/'
MODEL_NWORD_VARS = '../model_dir/nword_vars'
MODEL_VOCAB_PROCESSOR_VARS = '../model_dir/vocab_processor_vars'

MAX_DOCUMENT_LENGTH = 500
N_CLASSES = 5
EMBEDDING_SIZE = 100
N_FILTERS = 10
WINDOW_SIZE = 10

FILTER_SHAPE1 = [WINDOW_SIZE, EMBEDDING_SIZE]
FILTER_SHAPE2 = [WINDOW_SIZE, N_FILTERS]

POOLING_WINDOW = 4
POOLING_STRIDE = 2

# Test runs with various learning rate. Results vary as data is shuffled. But overall, smaller learning rate gave better result.
# 0.05 gave ~ 30 - 35% accuracy at 200 steps
# 0.01 gave ~ 40 - ~70% accuracy at 200 steps
LEARNING_RATE = 0.01
STEPS = 300

def get_model_fn(n_classes, n_words):
    """

    """
    def model_fn(features, target):

        target = tf.one_hot(target, n_classes, 1, 0)
        word_vectors = tf.contrib.layers.embed_sequence(
            features, vocab_size=n_words, embed_dim=EMBEDDING_SIZE, scope='words')

        word_vectors = tf.expand_dims(word_vectors, 3)

        # Layer 1
        with tf.variable_scope('layer1'):
            conv1 = tf.contrib.layers.convolution2d(
                word_vectors, N_FILTERS, FILTER_SHAPE1, padding='VALID')
            conv1 = tf.nn.relu(conv1)
            pool1 = tf.nn.max_pool(
                conv1,
                ksize=[1, POOLING_WINDOW, 1, 1],
                strides=[1, POOLING_STRIDE, 1, 1],
                padding='SAME')
            # Transpose matrix so that n_filters from convolution becomes width.
            pool1 = tf.transpose(pool1, [0, 1, 3, 2])

        # Layer 2
        with tf.variable_scope('layer2'):
            conv2 = tf.contrib.layers.convolution2d(
                pool1, N_FILTERS, FILTER_SHAPE2, padding='VALID')
            pool2 = tf.squeeze(tf.reduce_max(conv2, 1), squeeze_dims=[1])

        logits = tf.contrib.layers.fully_connected(pool2, n_classes, activation_fn=None)
        loss = tf.contrib.losses.softmax_cross_entropy(logits, target)

        train_op = tf.contrib.layers.optimize_loss(
          loss,
          tf.contrib.framework.get_global_step(),
          optimizer='Adam',
          learning_rate=LEARNING_RATE)

        return ({
          'relevance': tf.argmax(logits, 1),
          'prob': tf.nn.softmax(logits)
        }, loss, train_op)

    return model_fn


def main(unused_argv):
    # for testing
    if REMOVE_OLD_MODEL:
        # Remove old model
        shutil.rmtree(MODEL_DIR)
        os.mkdir(MODEL_DIR)

    # Read in the training data set.
    dataset = pd.read_csv(DATA_SET_FILE, header=None)

    # Perform random shuffle on the dataset. Extract 80% of the dataset as training data and 20% as test data.
    # This is only to simulate more random data. Should not be used after training.
    dataset.sample(frac=1)
    training_dataset = dataset[0:400]
    test_dataset = dataset.drop(training_dataset.index)

    # Training and test datasets contain short news description.
    x_train = training_dataset[1]
    y_train = training_dataset[0]
    x_test = test_dataset[1]
    y_test = test_dataset[0]

    # Tensorflow has a preprocessing module that contains the Vocabulary Processor class, which maps documents of word id sequences
    # Vocabulary processor has fit_transform and fit methods which are used below.
    # Class documentation is: http://tflearn.org/data_utils/
    vocab_processor = tf.contrib.learn.preprocessing.VocabularyProcessor(MAX_DOCUMENT_LENGTH)
    x_train = np.array(list(vocab_processor.fit_transform(x_train)))
    x_test = np.array(list(vocab_processor.transform(x_test)))

    # vocabulary_ is the only attribute of the Vocabulary Processor class, containing the vocabularies from preprocessing
    n_words = len(vocab_processor.vocabulary_)
    print('Total words: %d' % n_words) # test

    # Save variables from vocab_processor.
    with open(MODEL_NWORD_VARS, 'w') as f:
        pickle.dump(n_words, f)

    vocab_processor.save(MODEL_VOCAB_PROCESSOR_VARS)

    # tf.contrib.learn.Estimator is the basic TensorFlow model trainer. It's instantiated with a given model_fn.
    # Its documentation can be found here:
    # https://www.tensorflow.org/versions/r1.0/api_docs/python/tf/contrib/learn/Estimator
    # model, graph, and vars will be saved for server to use.
    classifier = tf.contrib.learn.Estimator(
        model_fn=get_model_fn(N_CLASSES, n_words),
        model_dir=MODEL_DIR
    )

    # Train model using the training dataset
    classifier.fit(x_train, y_train, steps=STEPS)

    # Evaluate model using the test dataset
    y_predicted = [
        p['relevance'] for p in classifier.predict(x_test, as_iterable=True)
    ]
    print y_predicted

    # For testing, output the accuracy score
    score = metrics.accuracy_score(y_test, y_predicted)
    print('Accuracy: {0:f}'.format(score))

if __name__ == '__main__':
    tf.app.run(main=main)
