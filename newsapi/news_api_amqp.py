# -*- coding: utf-8 -*-
import json
import pika

class CloudAMQPClient:
    """ A helper class based on Rabbit MQ using the pika python module."""
    def __init__(self, cloud_amqp_url, queue_name):
        self.cloud_amqp_url = cloud_amqp_url
        self.queue_name = queue_name
        self.params = pika.URLParameters(cloud_amqp_url)
        self.params.socket_timeout = 3
        self.connection = pika.BlockingConnection(self.params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue = queue_name)

    def send_message(self, message):
        if message is None:
            raise Exception("Cannot send a null message")
        try:
            self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=message);
        except Exception as e:
            raise e
        print "[x] Sent message to %s" % (self.queue_name)

    def get_message(self):
        method_frame, header_frame, body = self.channel.basic_get(self.queue_name)
        if method_frame:
            self.channel.basic_ack(method_frame.delivery_tag)
            return json.loads(body)
        else:
            print '[x] No message returned from queue: %s' % self.queue_name
            return None

    def sleep(self, seconds):
        self.connection.sleep(seconds)
