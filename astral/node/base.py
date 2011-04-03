"""
astral.node.base
==========

Node Base Class.

"""
import threading
import json

import astral.api.app
from astral.models import Node, session, Event
from astral.conf import settings
from astral.exceptions import NetworkError
from astral.api.client import NodesAPI

import logging
log = logging.getLogger(__name__)


class LocalNode(object):
    def run(self, uuid_override=None, **kwargs):
        # Kind of a hack to make sure logging is set up before we do anything
        settings.LOGGING_CONFIG
        self.load_this_node(uuid_override)
        self.BootstrapThread(self.node).start()
        self.DaemonThread().start()
        try:
            astral.api.app.run()
        except: # tolerate the bare accept here to make sure we always shutdown
            self.shutdown()

    def load_this_node(self, uuid_override):
        if not getattr(self, 'node', None):
            self.node = Node.me(uuid_override=uuid_override)
            session.commit()

    def shutdown(self):
        if self.node.supernode:
            log.info("Unregistering ourself (%s) from the web server",
                    self.node)
            NodesAPI(settings.ASTRAL_WEBSERVER).unregister(
                    self.node.absolute_url())

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
                nodes = NodesAPI(base_url).list()
            except NetworkError, e:
                log.warning("Can't connect to server: %s", e)
            else:
                log.debug("Nodes returned from the server: %s", nodes)
                nodes = [Node.from_dict(node) for node in nodes]

        def register_with_supernode(self):
            Node.update_supernode_rtt()
            # TODO hacky hacky hacky. moving query inside of the node causes
            # SQLAlchemy session errors.
            session.commit()
            session.close_all()
            self.node = Node.me()
            if not self.node.supernode:
                self.node.primary_supernode = Node.closest_supernode()
                if not self.node.primary_supernode:
                    self.node.supernode = True
                    try:
                        NodesAPI(settings.ASTRAL_WEBSERVER).register(
                                self.node.to_dict())
                    except NetworkError, e:
                        log.warning("Can't connect to server to register as a "
                                "supernode: %s", e)
                else:
                    try:
                        NodesAPI(self.node.primary_supernode.uri()).register(
                                self.node.to_dict())
                    except NetworkError, e:
                        # TODO try another?
                        log.warning("Can't connect to supernode %s to register"
                                ": %s", self.node.primary_supernode, e)
                    else:
                        self.load_dynamic_bootstrap_nodes(
                                self.node.primary_supernode.uri())
            else:
                # TODO register with all (some?) other supernodes. supernode
                # cool kids club.
                pass
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
                Event(message=json.dumps({'type': "update"}))
                time.sleep(10)
