# -*- coding: utf-8 -*-
import json
import logging
import os
import sys
import time
import urllib2

from crawler_stats import CrawlerStats
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'newsapi'))
from news_api_amqp import CloudAMQPClient

HTML_DOWNLOAD_DIR = 'html'

AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_DOWNLOAD_QUEUE_NAME = 'cs6913_crawler_download'
AMQP_SLEEP_IN_SECONDS = 10

def download_news(msg):
    if msg is None:
        return

    # start the crawler log capture
    crawlStats = CrawlerStats()

    url = msg['url']
    digest = msg['digest'].replace('/', '___')
    filename = os.path.join(os.path.dirname(__file__), '..', HTML_DOWNLOAD_DIR, digest)

    try:
        # print msg
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'wse_crawler')
        res = urllib2.urlopen(req)
        content = res.read()

    except urllib2.HttpError, exp:
        logging.error('Http Error. Url: %s. %s' % (url, exp))
        crawlStats.add(msg['url'], msg['relevance'], msg['digest'], 0, exp.getcode(), str(exp))
    except IOError as ioe:
        logging.error('IO Error. Url: %s. %s' % (url, ioe))
        crawlStats.add(msg['url'], msg['relevance'], msg['digest'], 0, 1, str(ioe))
    else:

        # write the crawled page to file
        statusCode = res.getcode()
        filesize = len(content)
        with open(filename, 'w+') as f:
            f.write(content)

        crawlStats.add(msg['url'], msg['relevance'], msg['digest'], filesize, statusCode, '')
        logging.info('Crawl. Url: %s' % (url))


""" while loop that constantly listens at the message queue and retrieves next news to download
    This module provides graceful shutdown.
"""
def main():
    amqp_download_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_DOWNLOAD_QUEUE_NAME)

    startTime = time.time()

    try:
        while True:
            if amqp_download_client is not None:
                msg = amqp_download_client.get_message()

                if msg is not None:
                    try:
                        download_news(msg)
                    except Exception as e:
                        pass
            amqp_download_client.sleep(AMQP_SLEEP_IN_SECONDS)

    except KeyboardInterrupt as kbint:
        print '\nKeyboardInterrupt detected. Writing crawl status... and terminating'
        endTime = time.time()
        duration = endTime - startTime

        crawlStats = CrawlerStats()
        crawlStats.writeStats(duration)
        logging.info('Crawler download ended\n')
        sys.exit(0)

if __name__ == '__main__':
    CRAWLER_LOG = 'crawler.log'
    CRAWLER_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
    logging.basicConfig(filename=CRAWLER_LOG, level=logging.INFO, format=CRAWLER_LOG_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('Crawler download started\n')

    main()
