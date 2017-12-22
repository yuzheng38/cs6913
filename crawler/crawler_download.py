# -*- coding: utf-8 -*-
import logging
import sys
import os
import time
import json
import urllib2

AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_DOWNLOAD_QUEUE_NAME = 'cs6913_crawler_download'
AMQP_SLEEP_IN_SECONDS = 10

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'newsapi'))
from news_api_amqp import CloudAMQPClient

HTML_DOWNLOAD_DIR = 'html'

def download_news(msg):
    if msg is None:
        return

    # get the logger, robot, and do the download.. use stats to log result
    # get the message url
    url = msg['url']
    digest = msg['digest'].replace('/', '___')
    filename = os.path.join(os.path.dirname(__file__), '..', HTML_DOWNLOAD_DIR, digest)

    try:
        print 'assume saving file.. it\'s working'
        # req = urllib2.Request(url)
        # req.add_header('User-Agent', 'wse_crawler')
        # res = urllib2.urlopen(req)
        # with open(filename, 'w+') as f:
        #     f.write(res.read())
    except urllib2.HttpError, exp:
        print 'me'
        # do some logging
    except IOError as ioe:
        print 'me'
        # do some other logging


def main():
    amqp_download_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_DOWNLOAD_QUEUE_NAME)

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
        # clean up !!!!!!
        sys.exit(0)

if __name__ == '__main__':
    main()


# ###### create a logger here. ###
# CRAWLER_LOG = 'crawler.log'
# CRAWLER_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
# logging.basicConfig(filename=CRAWLER_LOG, level=logging.DEBUG, format=CRAWLER_LOG_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
# logger = logging.getLogger('global_logger')
# ###### logger works OK now ####
