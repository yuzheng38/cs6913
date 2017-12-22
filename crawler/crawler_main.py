# -*- coding: utf-8 -*-
import json
import logging
import os
import pyjsonrpc
import sys
import time

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'newsapi'))
from crawler_queue import CrawlerPQueue
from news_api_amqp import CloudAMQPClient

CLASSIFIER_URL = 'http://localhost:6060'
classifier_client = pyjsonrpc.HttpClient(CLASSIFIER_URL)

AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_QUEUE_NAME = 'cs6913_news_api'
AMQP_DOWNLOAD_QUEUE_NAME = 'cs6913_crawler_download'
AMQP_SLEEP_IN_SECONDS = 5
CRAWLER_SLEEP_IN_SECONDS = 1

amqp_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_QUEUE_NAME)
amqp_download_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_DOWNLOAD_QUEUE_NAME)

RELEVANCE_THRESHOLD = 1

def main():
    pqueue = CrawlerPQueue()

    try:
        while True:
            news = amqp_client.get_message()

            if news is None:
                time.sleep(CRAWLER_SLEEP_IN_SECONDS)   # throttle crawler if there's no new news in the queue
                continue

            if news['description'] is None:
                news['description'] = news['title']

            relevance = classifier_client.call('classify', json.dumps(news['description']))
            news['relevance'] = relevance

            if relevance >= RELEVANCE_THRESHOLD:
                relevance = 5 - relevance   # 5 - is important
                pqueue.put((relevance, news))

            if not pqueue.empty():
                nextNews = list(pqueue.get())[1]
                amqp_download_client.send_message(json.dumps(nextNews))

            amqp_download_client.sleep(AMQP_SLEEP_IN_SECONDS)

    except KeyboardInterrupt as kbint:
        print '\nKeyboardInterrupt detected. Crawler main pushing out the last items in priority queue\n'

        while not pqueue.empty():
            nextNews = list(pqueue.get())[1]
            amqp_download_client.send_message(json.dumps(nextNews))

        sys.exit(0)

if __name__ == '__main__':
    main()
