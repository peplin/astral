"""
astral.node.base
==========

Node Base Class.

"""
import threading

import astral.api.app
from astral.models import Node, session, Event
from astral.conf import settings
from astral.exceptions import NetworkError
from astral.api.client import Nodes

import logging
log = logging.getLogger(__name__)


class LocalNode(object):
    def run(self, **kwargs):
        # Kind of a hack to make sure logging is set up before we do anything
        settings.LOGGING_CONFIG
        self.load_this_node()
        self.BootstrapThread(self.node).start()
        self.DaemonThread().start()
        astral.api.app.run()

    def load_this_node(self):
        if not getattr(self, 'node', None):
            self.node = Node()
            session.commit()

    class BootstrapThread(threading.Thread):
        """Runs once at node startup to build knowledge of the network."""

        def __init__(self, node):
            super(LocalNode.BootstrapThread, self).__init__()
            self.node = node

        def load_static_bootstrap_nodes(self):
            log.info("Loading static bootstrap nodes %s",
                    settings.BOOTSTRAP_NODES)
            nodes = [Node.from_dict(node) for node in settings.BOOTSTRAP_NODES]
            session.commit()
            log.debug("Loaded static bootstrap nodes %s", nodes)

        def load_dynamic_bootstrap_nodes(self, base_url=None):
            base_url = base_url or settings.ASTRAL_WEBSERVER
            try:
                nodes = Nodes(base_url).get()
            except NetworkError, e:
                log.warning("Can't connect to server: %s", e)
            else:
                log.debug("Nodes returned from the server: %s", nodes)
                nodes = [Node.from_dict(node) for node in nodes]

        def register_with_supernode(self):
            self.node.update_primary_supernode()
            if not self.node.primary_supernode:
                self.node.supernode = True
                try:
                    Nodes(settings.ASTRAL_WEBSERVER).post(self.node.to_dict())
                except NetworkError, e:
                    log.warning("Can't connect to server to register as a "
                            "supernode: %s", e)
            else:
                Nodes(self.node.primary_supernode.absolute_url()).post(
                        self.node.to_dict())
                self.load_dynamic_bootstrap_nodes(
                        self.node.primary_supernode.absolute_url())
            session.commit()

        def run(self):
            self.load_static_bootstrap_nodes()
            self.load_dynamic_bootstrap_nodes()
            self.register_with_supernode()


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
                Event(message="Ping!")
                time.sleep(10)
