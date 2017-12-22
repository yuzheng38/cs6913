# -*- coding: utf-8 -*-
import datetime
import json
import threading

from singleton import singleton

@singleton
class CrawlerStats:
    def __init__(self):
        self.mutex = threading.Lock()
        self._records = []
        self._stats = {
            'total_download': 0,
            'total_size': 0,
            'total_error': 0,
            'total_time': None
        }

    def add(self, url, relevance, fn, fsize, http_res_code, http_error=""):
        timestamp = datetime.datetime.utcnow().strftime("%m/%d/%Y %H:%M:%S")
        rec = {
            "url": url,
            "timestamp": timestamp,
            "relevance": relevance,
            "filename": fn,
            "filesize": fsize,
            "httpcode": http_res_code,
            "httperr": http_error
        }

        self.mutex.acquire()
        self._records.append(rec)
        self._stats['total_download'] += 1
        self._stats['total_size'] += fsize
        if http_error:
            self._stats['total_error'] += 1
        self.mutex.release()

    def writeStats(self, totalTime):
        timestamp = datetime.datetime.utcnow().strftime("%m-%d-%Y-%H-%M-%S")
        stats_filename = timestamp + '.stats'
        self._stats['total_time'] = totalTime
        self._stats['total_size'] = '{0:.2f}'.format(self._stats['total_size'] / 1024)

        with open(stats_filename, 'w') as f:
            for rec in self._records:
                json.dump(rec, f, sort_keys=True)
                f.write('\n')
            f.write('\n')
            json.dump(self._stats, f)

        # print 'Crawl stats written to file %s\n' % (stats_filename)
