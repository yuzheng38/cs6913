# -*- coding: utf-8 -*-

import numpy as np
import os
import pandas as pd
import pickle
import pyjsonrpc
import sys
import tensorflow as tf
import time

from tensorflow.contrib.learn.python.learn.estimators import model_fn
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# import the offline trained model
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'model_trainer'))
import trainer

# classifier server address
HOST = 'localhost'
PORT = 6060

# variables for the offline trained model are stored here
MODEL_DIR = '../model_dir'
MODEL_NWORD_VARS = '../model_dir/nword_vars'
MODEL_VOCAB_PROCESSOR_VARS = '../model_dir/vocab_processor_vars'

# global variables for model
MAX_DOCUMENT_LENGTH = 500
N_CLASSES = 5
n_words = 0
vocab_processor = None
classifier = None

""" Restore the variables used in the trained model """
def restoreTrainedModelVars():
    with open(MODEL_NWORD_VARS, 'r') as f:
        # retrieve n_words from the trained model. save it as a global var
        global n_words
        n_words = pickle.load(f)

    # restore the trained vocabulary processor using its saved vars.
    global vocab_processor
    vocab_processor = tf.contrib.learn.preprocessing.VocabularyProcessor.restore(MODEL_VOCAB_PROCESSOR_VARS)

""" Restore the model using the trained vocab processor and variables """
def restoreTrainedModel():
    # rebuild the classifier by passing in the model and the saved variables
    global classifier
    classifier = tf.contrib.learn.Estimator(
        model_fn = trainer.get_model_fn(N_CLASSES, n_words),
        model_dir = MODEL_DIR
    )

    # use the restored estimator to evaluate data, basically warm up. this is a missing feature in the version of tensorflow used.
    dataset = pd.read_csv('../data/training_data.csv', header=None)
    training_dataset = dataset[0:400]
    x_train = training_dataset[2]   # using 2nd column now
    x_train = np.array(list(vocab_processor.transform(x_train)))
    y_train = training_dataset[0]
    classifier.evaluate(x_train, y_train)

# Restore
restoreTrainedModelVars()
restoreTrainedModel()
print 'Classifier trained model loaded'

#############################################################
""" Watchdog event handler to monitor model changes """
class WatchDogEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        print 'Change detected'
        time.sleep(300)
        restoreTrainedModelVars()
        restoreTrainedModel()

observer = Observer()
handler = WatchDogEventHandler()
observer.schedule(handler, path=MODEL_DIR, recursive=False)
print 'Watchdog started'
observer.start()
##############################################################

""" Classifier server RPC handler """
class RequestHandler(pyjsonrpc.HttpRequestHandler):
    @pyjsonrpc.rpcmethod
    def classify(self, text):
        text_series = pd.Series([text])
        x = np.array(list(vocab_processor.transform(text_series)))
        print x

        y = [p['relevance'] for p in classifier.predict(x, as_iterable=True)]
        print y[0]  # get the top prediction #test
        return y[0]

# set up server and start server
server = pyjsonrpc.ThreadingHttpServer(
    server_address=(HOST, PORT),
    RequestHandlerClass=RequestHandler
)
print 'Classifier server started at %s:%s' % (str(HOST), str(PORT))
server.serve_forever()
