#!/usr/bin/env python

import threading
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
    from astral.api.handlers.events import queue_listener
    event_thread = threading.Thread(target=queue_listener)
    event_thread.daemon = True
    event_thread.start()

    app = NodeWebAPI()
    app.listen(settings.TORNADO_SETTINGS['port'])
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    run()
