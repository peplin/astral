#!/usr/bin/env python

import threading
import tornado.httpserver
import tornado.ioloop
import tornado.web

from astral.conf import settings
from urls import url_patterns

class NodeWebAPI(tornado.web.Application):
    def __init__(self, node=None):
        tornado.web.Application.__init__(self, url_patterns,
                **settings.TORNADO_SETTINGS)
        self.node = node


def run(node):
    from astral.api.handlers.events import queue_listener
    event_thread = threading.Thread(target=queue_listener)
    event_thread.daemon = True
    event_thread.start()

    app = NodeWebAPI(node)
    app.listen(settings.TORNADO_SETTINGS['port'])
    try:
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    run()
