from astral.api.handlers.base import BaseWebSocketHandler
from astral.models.event import EVENT_QUEUE

import logging
log = logging.getLogger(__name__)

# TODO make this thread safe if we have more than one event listener
LISTENERS = []


def queue_listener():
    while True:
        event = EVENT_QUEUE.get()
        log.debug("Found %s in event queue", event)
        for client in LISTENERS:
            log.debug("Sending %s to %s", event, client)
            client.write_message(unicode(event.message))
        EVENT_QUEUE.task_done()


class EventHandler(BaseWebSocketHandler):
    def open(self):
        log.debug("Websocket opened on %s", self.request.remote_ip)
        LISTENERS.append(self)

    def on_message(self, message):
        self.write_message("You said %s" % message)
   
    def on_close(self):
        log.debug("Websocket closed on %s", self.request.remote_ip)
        LISTENERS.remove(self)
