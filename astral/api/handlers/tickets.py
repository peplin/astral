
from tornado.web import HTTPError

from astral.api.handlers.base import BaseHandler
from astral.api.client import TicketsAPI
from astral.models import Ticket, Node, Stream, session
from astral.exceptions import NetworkError

import logging
log = logging.getLogger(__name__)


class TicketsHandler(BaseHandler):
    def _already_streaming(self, stream):
        return Ticket.get_by(stream=stream, source=Node.me())

    def _already_seeding(self, ticket):
        return Node.me() in [ticket.destination, ticket.stream.source]

    def _request_stream_from_node(self, stream, node, destination=None):
        try:
            created = TicketsAPI(node.uri()).create(stream.tickets_url(),
                    destination_uuid=Node.me().uuid)
        except NetworkError, e:
            log.info("Couldn't connect to %s to ask for %s -- deleting "
                    "the node from the database", node, stream) 
            log.debug("Node returned: %s", e)
            node.delete()
        else:
            if created:
                # TODO actually, the source returned might be different
                return Ticket(stream=stream, source=node)

    def _request_stream_from_watchers(self, stream, destination=None):
        for ticket in Ticket.query.filter_by(stream=stream):
            if self._already_seeding(ticket):
                return ticket
            else:
                new_ticket = self._request_stream_from_node(stream,
                        ticket.destination)
                if new_ticket:
                    return new_ticket

    def _request_stream_from_supernodes(self, stream, destination=None):
        for supernode in Node.supernodes():
            new_ticket = self._request_stream_from_node(stream, supernode)
            if new_ticket:
                return new_ticket

    def _request_stream_from_source(self, stream):
        return self._request_stream_from_node(stream, stream.source)

    def _request_stream(self, stream, destination=None):
        for possible_source_method in [self._request_stream_from_watchers,
                self._request_stream_from_supernodes,
                self._request_stream_from_source]:
            new_ticket = possible_source_method(stream)
            if new_ticket:
                return new_ticket

    def post(self, stream_id):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        stream = Stream.get_by(id=stream_id)
        destination_uuid = self.get_json_argument('destination_uuid', '')
        if destination_uuid:
            # TODO if we can't serve it, ask around on our network
            # TODO return the actual source, which in this default cause will be
            # ourselves
            # TODO may want to refactor the above methods so they could also be
            # used here - need to be able to pass in a final destination other
            # than ourselves
            # TODO if we're not a supernode, may not want to do a ton of query
            # work for another client, since they could do it themselves. the
            # point is to contact nodes we know of but they don't. perhaps
            # instead we return a list of nodes so they can do it themselves?
            # TODO observe some cap on the number of tickets, based on bandwidth
            node = Node.get_by(uuid=destination_uuid)
            if not node:
                raise HTTPError(404)
            Ticket(stream=stream, destination=node)
        else:
            if self._already_streaming(stream):
                self.redirect(stream.absolute_url())
            else:
                if stream.source != Node.me():
                    new_ticket = self._request_stream(stream)
                    if not new_ticket:
                        raise HTTPError(412)
                Ticket(stream=stream)
        session.commit()
        self.redirect(stream.absolute_url())

    def get(self):
        """Return a JSON list of all known tickets."""
        self.write({'tickets': [ticket.to_dict()
                for ticket in Ticket.query.all()]})
