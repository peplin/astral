"""
astral.node.base
==========

Node Base Class.

"""

import astral.api.app
from astral.models import Node, Ticket, session
from astral.conf import settings
from astral.api.client import NodesAPI, TicketsAPI
from astral.node.bootstrap import BootstrapThread
from astral.node.daemon import DaemonThread
from astral.node.stream import StreamingThread
from astral.node.tunnel import TunnelControlThread

import logging
log = logging.getLogger(__name__)


class LocalNode(object):
    def run(self, uuid_override=None, upstream_limit=None, **kwargs):
        # Kind of a hack to make sure logging is set up before we do anything
        settings.LOGGING_CONFIG
        self.upstream_limit = upstream_limit
        self.uuid = uuid_override
        self.bootstrap()
        StreamingThread().start()
        TunnelControlThread().start()
        DaemonThread().start()

        try:
            astral.api.app.run(self)
        finally: # tolerate the bare accept here to make sure we always shutdown
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
            if node != Node.me().primary_supernode:
                log.info("Unregistering from %s", node)
                NodesAPI(node.uri()).unregister(self.node().absolute_url())

    def _cancel_tickets(self):
        for ticket in Ticket.query.filter_by(source=Node.me()).filter(
                Ticket.destination != Node.me()):
            log.info("Cancelling %s", ticket)
            if ticket.destination:
                TicketsAPI(ticket.destination.uri()).cancel(ticket.absolute_url())

        for ticket in Ticket.query.filter_by(destination=Node.me()).filter(
                Ticket.source != Node.me()):
            log.info("Cancelling %s", ticket)
            if ticket.source:
                TicketsAPI(ticket.source.uri()).cancel(ticket.absolute_url())
        Ticket.query.delete()

    def shutdown(self):
        self._unregister_from_origin()
        self._unregister_from_supernode()
        self._cancel_tickets()
        self._unregister_from_all()
        session.commit()

    def bootstrap(self):
        BootstrapThread(node=self.node,
                upstream_limit=self.upstream_limit).start()
