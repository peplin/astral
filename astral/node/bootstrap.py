import threading

from astral.models import Node, session
from astral.exceptions import NetworkError
from astral.node.upstream import UpstreamCheckThread
from astral.conf import settings
from astral.api.client import NodesAPI

import logging
log = logging.getLogger(__name__)

class BootstrapThread(threading.Thread):
    """Runs once at node startup to build knowledge of the network."""

    def __init__(self, node, upstream_limit):
        super(BootstrapThread, self).__init__()
        self.node = node
        self.upstream_limit = upstream_limit

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
            for node in nodes:
                # TODO if we find ourselves with an old IP, need to update
                if self.node().conflicts_with(node):
                    log.warn("Received %s which conflicts with us (%s) "
                            "-- telling web server to kill it")
                    NodesAPI(base_url).unregister(
                            Node.absolute_url(node['uuid']))
                else:
                    node = Node.from_dict(node)
                    log.info("Stored %s from %s", node, base_url)

    def register_with_supernode(self):
        Node.update_supernode_rtt()
        # TODO hacky hacky hacky. moving query inside of the node causes
        # SQLAlchemy session errors.
        session.commit()
        session.close_all()

        if not self.node().supernode:
            self.node().primary_supernode = Node.closest_supernode()
            if not self.node().primary_supernode:
                self.node().supernode = True
                log.info("Registering %s as a supernode, none others found",
                        self.node())
                try:
                    NodesAPI(settings.ASTRAL_WEBSERVER).register(
                            self.node().to_dict())
                except NetworkError, e:
                    log.warning("Can't connect to server to register as a "
                            "supernode: %s", e)
            else:
                try:
                    NodesAPI(self.node().primary_supernode.uri()).register(
                            self.node().to_dict())
                except NetworkError, e:
                    # TODO try another?
                    log.warning("Can't connect to supernode %s to register"
                            ": %s", self.node().primary_supernode, e)
                else:
                    self.load_dynamic_bootstrap_nodes(
                            self.node().primary_supernode.uri())
        else:
            for supernode in Node.supernodes():
                try:
                    NodesAPI(supernode.uri()).register(
                            self.node().to_dict())
                except NetworkError, e:
                    log.warning("Can't connect to supernode %s: %s",
                            supernode, e)
                    supernode.delete()
        session.commit()

    def run(self):
        UpstreamCheckThread(self.node, self.upstream_limit).run()
        self.load_static_bootstrap_nodes()
        self.load_dynamic_bootstrap_nodes()
        self.register_with_supernode()
