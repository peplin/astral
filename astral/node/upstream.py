import threading

from astral.conf import settings
from astral.exceptions import NetworkError

import logging
log = logging.getLogger(__name__)

class UpstreamCheckThread(threading.Thread):
    """Runs once at node startup to check the total upstream to the origin
    server.
    """
    def __init__(self, node, upstream_limit):
        super(UpstreamCheckThread, self).__init__()
        self.node = node
        self.upstream_limit = upstream_limit

    def run(self):
        if not self.upstream_limit:
            try:
                self.node().update_upstream(settings.ASTRAL_WEBSERVER)
                log.info("Determined maximum upstream bandwidth to be "
                        "%d KB/s", self.node().upstream)
            except NetworkError:
                log.warning("Unable to connect to origin webserver to "
                        "determine upstream bandwidth")
        else:
            self.node().upstream = self.upstream_limit
            log.info("Using manually specified maximum upstream %s KB/s",
                    self.node().upstream)

