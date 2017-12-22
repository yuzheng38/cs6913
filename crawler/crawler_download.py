# -*- coding: utf-8 -*-
import logging
import sys
import os
import time
import json
import requests

AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_DOWNLOAD_QUEUE_NAME = 'cs6913_crawler_download'
AMQP_SLEEP_IN_SECONDS = 10

def download_news(msg):
    if msg is None or len(msg) == 0:
        return


    # get the logger, robot, and do the download

    print msg
    print msg['url']

def main():
    amqp_download_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_DOWNLOAD_QUEUE_NAME)
    
    try:
        while True:
            if amqp_download_client is not None:
                msg = amqp_download_client.get_message()

                if msg is not None:
                    try:
                        handle_message(msg)
                    except Exception as e:
                        # loggg
                        pass
            amqp_download_client.sleep(AMQP_SLEEP_IN_SECONDS)
    except KeyboardInterrupt as kbint:
        # clean up !!!!!!
        sys.exit(0)

if __name__ == '__main__':
    main()
