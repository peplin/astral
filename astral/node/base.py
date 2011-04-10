"""
astral.node.base
==========

Node Base Class.

"""
import threading
import json

import astral.api.app
from astral.models import Node, session, Event, Ticket
from astral.conf import settings
from astral.exceptions import NetworkError
from astral.api.client import NodesAPI, TicketsAPI

import logging
log = logging.getLogger(__name__)


class LocalNode(object):
    def run(self, uuid_override=None, upstream_limit=None, **kwargs):
        # Kind of a hack to make sure logging is set up before we do anything
        settings.LOGGING_CONFIG
        self.upstream_limit = upstream_limit
        self.uuid = uuid_override
        self.BootstrapThread(node=self.node,
                upstream_limit=self.upstream_limit).start()
        self.DaemonThread().start()
        try:
            astral.api.app.run()
        except: # tolerate the bare accept here to make sure we always shutdown
            self.shutdown()

    def node(self):
        return Node.get_by(uuid=self.uuid) or Node.me(uuid_override=self.uuid)

    def _unregister_from_origin(self):
        if self.node().supernode:
            log.info("Unregistering ourself (%s) from the web server",
                    self.node())
            NodesAPI(settings.ASTRAL_WEBSERVER).unregister(
                    self.node().absolute_url())

    def _unregister_from_supernode(self):
        if self.node().primary_supernode:
            log.info("Unregistering %s from our primary supernode (%s)",
                    self.node(), self.node().primary_supernode)
            NodesAPI(self.node().primary_supernode.uri()).unregister(
                    self.node().absolute_url())

    def _unregister_from_all(self):
        for node in Node.not_me():
            log.info("Unregistering from %s", node)
            NodesAPI(node.uri()).unregister(self.node().absolute_url())

    def _cancel_tickets(self):
        for ticket in Ticket.query.filter_by(source=Node.me()):
            log.info("Cancelling %s", ticket)
            TicketsAPI(ticket.destination.uri()).delete(ticket.absolute_url())

        for ticket in Ticket.query.filter_by(destination=Node.me()):
            log.info("Cancelling %s", ticket)
            TicketsAPI(ticket.source.uri()).delete(ticket.absolute_url())

    def shutdown(self):
        self._unregister_from_origin()
        self._unregister_from_supernode()
        self._cancel_tickets()
        self._unregister_from_all()

    class UpstreamCheckThread(threading.Thread):
        """Runs once at node startup to check the total upstream to the origin
        server.
        """
        def __init__(self, node, upstream_limit):
            super(LocalNode.UpstreamCheckThread, self).__init__()
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

    class BootstrapThread(threading.Thread):
        """Runs once at node startup to build knowledge of the network."""

        def __init__(self, node, upstream_limit):
            super(LocalNode.BootstrapThread, self).__init__()
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
            LocalNode.UpstreamCheckThread(self.node, self.upstream_limit).run()
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
