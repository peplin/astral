#!/usr/bin/env python

import tornado.httpserver
import tornado.ioloop
import tornado.web

from astral.conf import settings
from urls import url_patterns

class NodeWebAPI(tornado.web.Application):
    def __init__(self):
        tornado.web.Application.__init__(self, url_patterns,
                **settings.TORNADO_SETTINGS)


def run():
    app = NodeWebAPI()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(settings.TORNADO_SETTINGS['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()
