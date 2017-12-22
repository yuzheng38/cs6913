from singleton import singleton

import ConfigParser
import sys
import logging


CONFIG_FILE = 'crawler.configs'

@singleton
class CrawlerConfig:
    _mimeTypeBlacklist = []
    _mimeSubtypeBlacklist = []
    _mimeSubtypeWhitelist = []
    _suffixBlacklist = []
    _numSeeds = 0
    _numWorkerThreads = 0

    def __init__(self):
        configParser = ConfigParser.ConfigParser()
        configParser.read(CONFIG_FILE)

        try:
            mimeTypeBL = configParser.get('CrawlerConfigs', 'MimeTypeBlacklist')
            mimeSubtypeWL = configParser.get('CrawlerConfigs', 'MimeSubtypeWhitelist')
            mimeSubtypeBL = configParser.get('CrawlerConfigs', 'MimeSubtypeBlacklist')
            suffixBL = configParser.get('CrawlerConfigs', 'SuffixBlacklist')
            numSeeds = configParser.getint('CrawlerConfigs', 'NumCrawlerSeeds')
            numThreads = configParser.getint('CrawlerConfigs', 'NumWorkerThreads')
        except Exception, ex:
            print('Error reading crawler configurations ' + str(ex))
            sys.exit(1)
        else:
            if len(mimeTypeBL) > 0:
                mimes = mimeTypeBL.split(',')
                for mime in mimes:
                    self._mimeTypeBlacklist.append(mime.strip().lower())

            if len(mimeSubtypeWL) > 0:
                mimes = mimeSubtypeWL.split(',')
                for mime in mimes:
                    self._mimeSubtypeWhitelist.append(mime.strip().lower())

            if len(mimeSubtypeBL) > 0:
                mimes = mimeSubtypeBL.split(',')
                for mime in mimes:
                    self._mimeSubtypeBlacklist.append(mime.strip().lower())

            if len(suffixBL) > 0:
                suffices = suffixBL.split(',')
                for suffix in suffices:
                    self._suffixBlacklist.append(suffix.strip().lower())

            if numSeeds:
                self._numSeeds = numSeeds

            if numThreads:
                self._numWorkerThreads = numThreads

    def getMimeTypeBlacklist(self):
        return self._mimeTypeBlacklist

    def getMimeSubtypeBlacklist(self):
        return self._mimeSubtypeBlacklist

    def getMimeSubtypeWhitelist(self):
        return self._mimeSubtypeWhitelist

    def getSuffixBlacklist(self):
        return self._suffixBlacklist

    def getNumSeeds(self):
        return self._numSeeds

    def getNumWorkerThreads(self):
        return self._numWorkerThreads

    def isValidMimeType(self, other):
        if other.strip().lower() in self._mimeSubtypeBlacklist:
            return False
        if other.strip().lower() in self._mimeSubtypeWhitelist:
            return True
        mimeTypes = other.split('/')
        if mimeTypes[0].strip().lower() in self._mimeTypeBlacklist:
            return False
        return True

##### Test
# if __name__ == '__main__':
#     test = CrawlerConfig()
#     print test.getMimeTypeBlacklist()
#     print test.getMimeSubtypeBlacklist()
#     print test.getMimeSubtypeWhitelist()
#     print test.getSuffixBlacklist()
#     print test.getNumSeeds()
#     print test.getNumWorkerThreads()
#
#     print test.isValidMimeType('image')
#     print test.isValidMimeType('text/html')
#
# def testLog():
#     logging.info('this is a message from config')
