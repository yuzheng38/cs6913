# -*- coding: utf-8 -*-
import logging
import crawler_config
import pyjsonrpc
import sys
import os
import time
import threading
import json

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'newsapi'))
from crawler_queue import CrawlerPQueue
from news_api_amqp import CloudAMQPClient

CLASSIFIER_URL = 'http://localhost:6060'
classifier_client = pyjsonrpc.HttpClient(CLASSIFIER_URL)

AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_QUEUE_NAME = 'cs6913_news_api'
AMQP_DOWNLOAD_QUEUE_NAME = 'cs6913_crawler_download'
AMQP_SLEEP_IN_SECONDS = 10

amqp_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_QUEUE_NAME)
amqp_download_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_DOWNLOAD_QUEUE_NAME)

RELEVANCE_THRESHOLD = 0
CRAWLER_SLEEP_IN_SECONDS = 5

def main():
    # config = CrawlerConfig()
    pqueue = CrawlerPQueue()
    # stats = CrawlerStats()
    # robots = CrawlerRobot()

    while True:
        news = amqp_client.get_message()

        if news is None:
            time.sleep(CRAWLER_SLEEP_IN_SECONDS)   # throttle crawler if there's no pending news to crawl
            continue

        if news['description'] is None:
            news['description'] = news['title']

        relevance = classifier_client.call('classify', json.dumps(news['description']))
        # print relevance #test
        # print news['url'] #test

        if relevance > RELEVANCE_THRESHOLD:
            pqueue.put((relevance, news))

        # get from pqueue and send it out to download queue.. need to run download server
        while pqueue.empty() != True:
            nextNews = pqueue.get()
            amqp_download_client.send_message(nextNews)

        amqp_download_client.sleep(AMQP_SLEEP_IN_SECONDS)

if __name__ == '__main__':
    main()


# ###### create a logger here. ###
# CRAWLER_LOG = 'crawler.log'
# CRAWLER_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
# logging.basicConfig(filename=CRAWLER_LOG, level=logging.DEBUG, format=CRAWLER_LOG_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
# logger = logging.getLogger('global_logger')
# ###### logger works OK now ####
