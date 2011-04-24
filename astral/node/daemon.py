import threading

from astral.models import Ticket

import logging
log = logging.getLogger(__name__)

class DaemonThread(threading.Thread):
    """Background thread for garbage collection and other periodic tasks
    outside the scope of the web API.
    """
    def __init__(self, tunnel_controller):
        super(DaemonThread, self).__init__()
        self.daemon = True
        self.tunnel_controller = tunnel_controller

    def _cleanup_unconfirmed_tickets(self):
        query = Ticket.unconfirmed()
        query = Ticket.old(query=query)
        for ticket in query:
            log.info("Expiring unconfirmed ticket %s", ticket)
            ticket.delete()

    def run(self):
        import time
        while self.is_alive():
            self._cleanup_unconfirmed_tickets()
            # TODO would like this to happen on demand, and not have to wait for
            # this to spin up
            self.tunnel_controller.open_new_tunnels()
            self.tunnel_controller.close_expired_tunnels()
            time.sleep(10)
