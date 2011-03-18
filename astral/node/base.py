"""
astral.node.base
==========

Node Base Class.

"""
import threading

import astral.api
from astral.models import Node
from astral.conf import settings
from astral.exceptions import OriginWebserverError
from astral.api.client import Nodes

import logging
log = logging.getLogger(__name__)


class LocalNode(object):
    def run(self, **kwargs):
        # TODO have to trigger loading of the settings with this, otherwise we
        # have a race condition between the threads and an exception can occur -
        # how can we protect the settings, specifically the log configuration?
        settings.ASTRAL_WEBSERVER
        self.BootstrapThread().start()
        self.DaemonThread().start()
        astral.api.run()

    class BootstrapThread(threading.Thread):
        """Runs once at node startup to build knowledge of the network."""
        def load_static_bootstrap_nodes(self):
            log.info("Loading static bootstrap nodes %s",
                    settings.BOOTSTRAP_NODES)
            nodes = [Node.from_json(node) for node in settings.BOOTSTRAP_NODES]
            log.debug("Loaded static bootstrap nodes %s", nodes)

        def load_dynamic_bootstrap_nodes(self):
            try:
                nodes = Nodes().get()
            except OriginWebserverError, e:
                log.exception(e)
            else:
                log.debug("Nodes returned from the web server: %s", nodes)
                nodes = [Node.from_json(node) for node in nodes]

        def run(self):
            self.load_static_bootstrap_nodes()
            self.load_dynamic_bootstrap_nodes()
            # TODO find the closests supernode, POST ourselves to it


    class DaemonThread(threading.Thread):
        """Background thread for garbage collection and other periodic tasks
        outside the scope of the web API.
        """
        def __init__(self):
            super(LocalNode.DaemonThread, self).__init__()
            self.daemon = True

        def run(self):
            import time
            while self.is_alive():
                log.debug("Daemon thread woke up")
                time.sleep(10)
