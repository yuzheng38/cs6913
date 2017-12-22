# -*- coding: utf-8 -*-
import hashlib
import json
import requests
import redis
import sys
import os

from news_api_amqp import CloudAMQPClient

NEWS_API_ARTICLES_ENDPOINT = 'https://newsapi.org/v1/articles'
NEWS_API_KEY = '538bed6d89214f48ac9808597bad6067'
NEWS_SOURCES = [
                'abc-news',
                'bbc-news',
                'cnn',
                'fox-news',
                'the-new-york-times',
                'google-news',
                'bloomberg',
                'the-washington-post'
                ]

def getNewsFromSources(sources, sortBy):
    articles = []

    for source in sources:
        payload = {
            'apiKey': NEWS_API_KEY,
            'source': source,
            'sortBy': sortBy
        }
        response = requests.get(NEWS_API_ARTICLES_ENDPOINT, params=payload)
        response_json = json.loads(response.content)

        if response_json is not None and response_json['status'] == 'ok':
            articles.extend(response_json['articles'])

    return articles


AMQP_QUEUE_URL = 'amqp://igtqfjjn:GuRV4SOZmqJG0cFn2cXU_dQ-q8iMfklV@fish.rmq.cloudamqp.com/igtqfjjn'
AMQP_QUEUE_NAME = 'cs6913_news_api'
AMQP_QUEUE_SLEEP = 5
amqp_client = CloudAMQPClient(AMQP_QUEUE_URL, AMQP_QUEUE_NAME)

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_TIMEOUT = 3600 * 24
redis_client = redis.StrictRedis(REDIS_HOST, REDIS_PORT)

def main():
    while True:
        news_list = getNewsFromSources(NEWS_SOURCES, 'top')

        news_count = 0

        for news in news_list:
            news_digest = hashlib.md5(news['title'].encode('utf-8')).digest().encode('base64')

            if redis_client.get(news_digest) is None:
                news['digest'] = news_digest
                news_count += 1

                redis_client.set(news_digest, 'True')
                redis_client.expire(news_digest, REDIS_TIMEOUT)

                amqp_client.send_message(json.dumps(news))

        print '[x] Fetched %d news from News API' % (news_count)
        amqp_client.sleep(AMQP_QUEUE_SLEEP)

if __name__ == '__main__':
    main()
