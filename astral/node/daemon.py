import threading

from astral.models import Ticket

import logging
log = logging.getLogger(__name__)

class DaemonThread(threading.Thread):
    """Background thread for garbage collection and other periodic tasks
    outside the scope of the web API.
    """
    def __init__(self):
        super(DaemonThread, self).__init__()
        self.daemon = True

    def _cleanup_unconfirmed_tickets(self):
        query = Ticket.unconfirmed()
        query = Ticket.old(query=query)
        for ticket in query:
            log.info("Expiring unconfirmed ticket %s", ticket)
            ticket.delete()

    def run(self):
        import time
        while self.is_alive():
            log.debug("Daemon thread woke up")
            self._cleanup_unconfirmed_tickets()
            time.sleep(10)
