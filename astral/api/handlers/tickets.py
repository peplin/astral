from tornado.web import HTTPError

from astral.conf import settings
from astral.api.handlers.base import BaseHandler
from astral.api.client import TicketsAPI, NodesAPI
from astral.models import Ticket, Node, Stream, session
from astral.exceptions import NetworkError

import logging
log = logging.getLogger(__name__)


class TicketsHandler(BaseHandler):
    def _already_streaming(self, stream, destination):
        return Ticket.get_by(stream=stream, source=Node.me(),
                destination=destination)

    def _already_seeding(self, ticket):
        return Node.me() in [ticket.destination, ticket.stream.source]

    def _request_stream_from_node(self, stream, node, destination=None):
        try:
            ticket_data = TicketsAPI(node.uri()).create(stream.tickets_url(),
                    destination_uuid=Node.me().uuid)
        except NetworkError, e:
            log.info("Couldn't connect to %s to ask for %s -- deleting "
                    "the node from the database", node, stream) 
            log.debug("Node returned: %s", e)
            node.delete()
        else:
            if ticket_data:
                source = Node.get_by(uuid=ticket_data['source'])
                if not source:
                    source_node_data = NodesAPI(node.uri()).get(
                            Node.absolute_url(source))
                    source = Node.from_dict(source_node_data)
                return Ticket(stream=stream, source=source,
                        source_port=ticket_data['source_port'])

    def _request_stream_from_watchers(self, stream, destination):
        tickets = []
        for ticket in Ticket.query.filter_by(stream=stream):
            if self._already_seeding(ticket):
                return [ticket]
            else:
                tickets.append(self._request_stream_from_node(stream,
                        ticket.destination))
        return filter(None, tickets)

    def _request_stream_from_supernodes(self, stream, destination):
        tickets = []
        for supernode in Node.supernodes():
            tickets.append(self._request_stream_from_node(stream, supernode))
        return filter(None, tickets)

    def _request_stream_from_source(self, stream, destination):
        return [self._request_stream_from_node(stream, stream.source)]

    def _request_stream(self, stream, destination):
        unconfirmed_tickets = []
        for possible_source_method in [self._request_stream_from_watchers,
                self._request_stream_from_supernodes,
                self._request_stream_from_source]:
            unconfirmed_tickets.extend(possible_source_method(stream,
                destination))
        return filter(None, unconfirmed_tickets)

    def post(self, stream_slug):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        # TODO break this method up, it's gotten quite big and complicated
        stream = Stream.get_by(slug=stream_slug)
        if not stream:
            raise HTTPError(404)
        destination_uuid = self.get_json_argument('destination_uuid', '')
        if destination_uuid:
            destination = Node.get_by(uuid=destination_uuid)
            if not destination:
                raise HTTPError(404)
        else:
            destination = Node.me()

        log.debug("Trying to create a ticket to serve %s to %s",
                stream, destination)
        new_ticket = self._already_streaming(stream, destination)
        if new_ticket:
            log.info("%s already has a ticket for %s: %s", destination,
                    stream, new_ticket)
            return self.redirect(new_ticket.absolute_url())

        # TODO base this on actual outgoing bandwidth
        if (Ticket.query.filter_by(source=Node.me()).count() >
                settings.OUTGOING_STREAM_LIMIT):
            log.info("Can't stream %s to %s, already at limit", stream,
                    destination)
            raise HTTPError(412)

        if stream.source != Node.me():
            # TODO before we ask others, we should check if we have a ticket
            # from somewhere with destination us. then we could offer that to
            # the requester. if so, create the ticket with the "source port" as
            # the destination port of the existing ticket. the requester will
            # grab use that destination as their tunnel's source, and pop open
            # another port on their localhost for the browser.

            # TODO if we're not a supernode, may not want to do a ton of query
            # work for another client, since they could do it themselves. the
            # point is to contact nodes we know of but they don't. perhaps
            # instead we return a list of nodes so they can do it themselves?
            unconfirmed_tickets = self._request_stream(stream, destination)
            if not unconfirmed_tickets:
                raise HTTPError(412)
            for ticket in unconfirmed_tickets:
                ticket.source.update_rtt()
            log.debug("Received %d unconfirmed tickets: %s",
                    len(unconfirmed_tickets), unconfirmed_tickets)

            closest = min(unconfirmed_tickets, key=lambda t: t.source.rtt)
            log.debug("Closest ticket of the unconfirmed ones is %s", closest)
            TicketsAPI(closest.source.uri()).confirm(closest.absolute_url())
            closest.confirmed = True
            session.commit()
            for ticket in set(unconfirmed_tickets) - set([closest]):
                TicketsAPI(ticket.source.uri()).cancel(ticket.absolute_url())
                ticket.delete()
            session.commit()
        else:
            closest = Ticket(stream=stream, destination=destination,
                confirmed=True)
            log.info("%s is the source of %s, created %s", destination,
                    stream, closest)
        session.commit()
        self.redirect(closest.absolute_url())

    def get(self):
        """Return a JSON list of all known tickets."""
        self.write({'tickets': [ticket.to_dict()
                for ticket in Ticket.query.all()]})
