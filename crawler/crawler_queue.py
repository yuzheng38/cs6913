# -*- coding: utf-8 -*-

from Queue import PriorityQueue
from singleton import singleton

@singleton
class CrawlerPQueue(PriorityQueue):
    def __init__(self):
        self.pq = PriorityQueue(-1)

    def qsize(self):
        return self.pq.qsize()

    def empty(self):
        return self.pq.empty()

    def full(self):
        return self.pq.full()

    def put(self, item):
        self.pq.put(item)

    def get(self):
        return self.pq.get()
