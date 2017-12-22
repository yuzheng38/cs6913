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


# if __name__ == '__main__':
#     testq = CrawlerPQueue()
#
#     testq.put((1, 'this should come out first'))
#     testq.put((5, 'this should come out last'))
#     testq.put((3, 'this should come out third'))
#     testq.put((4, 'this should come out fourth'))
#     testq.put((2, 'this should come out second'))
#
#     testq.put((3, 'this should come out third'))
#     testq.put((4, 'this should come out fourth'))
#     testq.put((2, 'this should come out second'))
#     testq.put((1, 'this should come out first'))
#     testq.put((5, 'this should come out last'))
#
#     print testq.qsize()
#
#     print testq.get()
#     print testq.get()
#     print testq.get()
#     print testq.get()
#     print testq.get()
#
#     print testq.getDownloadCount()
