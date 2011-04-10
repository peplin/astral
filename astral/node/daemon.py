import threading
import json

from astral.models import Event

import logging
log = logging.getLogger(__name__)

class DaemonThread(threading.Thread):
    """Background thread for garbage collection and other periodic tasks
    outside the scope of the web API.
    """
    def __init__(self):
        super(DaemonThread, self).__init__()
        self.daemon = True

    def run(self):
        import time
        while self.is_alive():
            log.debug("Daemon thread woke up")
            Event(message=json.dumps({'type': "update"}))
            time.sleep(10)
