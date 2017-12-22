import robotparser
import urlparse
from singleton import singleton
import threading
import logging

@singleton
class CrawlerRobot(object):
    def __init__(self):
        self.mutex = threading.Lock()
        self.robot_parsers = {}

    def _fetch_robot(self, url):
        parsed_url = urlparse.urlparse(url) #!!
        # REFERENCE: <scheme>://<netloc>/<path>;<params>?<query>#<fragment>
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc

        if netloc in self.robot_parsers:
            # print 'Already had a robot'
            return self.robot_parsers[netloc]
        else:
            robot_txt_url = ("%s://%s/robots.txt" % (scheme, netloc))
            robot_parser = robotparser.RobotFileParser()
            robot_parser.set_url(robot_txt_url)
            robot_parser.read()

            self.mutex.acquire()
            self.robot_parsers[netloc] = robot_parser
            self.mutex.release()

            return robot_parser

    def check_robot_txt(self, url):
        try:
            robot = self._fetch_robot(url)
            # print robot
            return robot.can_fetch('6913', url.encode('utf-8'))
        except Exception, exc:
            logger = logging.getLogger('global')
            logger.error('Robot parser. URL: %s Message: %s' % (url, str(exc)))
            return True

# if __name__ == '__main__':
#
#     CRAWLER_LOG = 'crawler.log'
#     CRAWLER_LOG_FORMAT = '%(asctime)s %(levelname)s %(message)s'
#     logging.basicConfig(filename=CRAWLER_LOG, level=logging.DEBUG, format=CRAWLER_LOG_FORMAT, datefmt='%m/%d/%Y %I:%M:%S %p')
#     logger = logging.getLogger('global')
#
#     crrobot = CrawlerRobot()
#     print crrobot.check_robot_txt('https://www.google.com')
#
#     crrobot2 = CrawlerRobot()
#     print 'is crrobot == crrobot2? '
#     print crrobot == crrobot2
#
#     print crrobot2.check_robot_txt('https://twitter.com')
#     print crrobot2.check_robot_txt('https://www.google.com/finance')
