# -*- coding: utf-8 -*-

from Queue import PriorityQueue
from singleton import singleton

@singleton
class CrawlerPQueue(PriorityQueue):
    def __init__(self):
        self.pq = PriorityQueue(-1)
        self.downloaded = {}
        self._downloadCount = 0

    def qsize(self):
        return self.pq.qsize()

    def empty(self):
        return self.pq.empty()

    def full(self):
        return self.pq.full()

    def put(self, item):
        if self.downloaded.has_key(item):
            return
        self.pq.put(item)
        self.downloaded[item] = 1   # dummy hack to dedup
        self._downloadCount += 1

    def get(self):
        return self.pq.get()

    def getDownloadCount(self):
        return self._downloadCount

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
