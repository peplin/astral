from tornado.web import HTTPError
import datetime

from astral.conf import settings
from astral.api.handlers.base import BaseHandler
from astral.api.client import TicketsAPI, NodesAPI, StreamsAPI
from astral.models import Ticket, Node, Stream, session
from astral.exceptions import NetworkError, NotFound

import logging
log = logging.getLogger(__name__)


class TicketsHandler(BaseHandler):
    @classmethod
    def _already_streaming(cls, stream, destination):
        return Ticket.get_by(stream=stream, destination=destination)

    @classmethod
    def _already_seeding(cls, ticket):
        return Node.me() in [ticket.destination, ticket.stream.source]

    @classmethod
    def _offer_ourselves(cls, stream, destination):
        tickets = Ticket.query.filter_by(source=Node.me())
        if (tickets.count() >= settings.OUTGOING_STREAM_LIMIT
                or Node.me().upstream and tickets.count()
                    * settings.STREAM_BITRATE > Node.me().upstream):
            log.info("Can't stream %s to %s, already at limit", stream,
                    destination)
            raise HTTPError(412)

        ticket = Ticket.get_by(stream=stream, destination=Node.me())
        if ticket:
            new_ticket = Ticket(stream=stream, destination=destination,
                    source_port=ticket.source_port, hops=ticket.hops + 1)
            log.info("We are receiving %s and have room to forward -- "
                "created %s to potentially forward to %s", stream, new_ticket,
                destination)
            return new_ticket

    @classmethod
    def _already_ticketed(cls, unconfirmed_tickets, node):
        """Check if we already have an unconfirmed ticket for the node we're
        looking for.
        """
        for unconfirmed_ticket in unconfirmed_tickets:
            if unconfirmed_ticket and unconfirmed_ticket.source == node:
                return True
        return False

    @classmethod
    def _request_stream_from_node(cls, stream, node, destination,
            existing_ticket=None):
        if not node or node == Node.me() or node == destination:
            return
        log.info("Requesting %s from the node %s, to be delivered to %s",
                stream, node, destination)
        try:
            ticket_data = TicketsAPI(node.uri()).create(stream.tickets_url(),
                    destination_uuid=destination.uuid)
        except NetworkError, e:
            log.info("Couldn't connect to %s to ask for %s -- deleting "
                    "the node from the database", node, stream)
            log.debug("Node returned: %s", e)
            # TODO since 412 returns a NetworkError, we would be deleting
            # everyone who can't deliver....
            #node.delete()
        else:
            if existing_ticket:
                return existing_ticket
            if ticket_data:
                source = Node.get_by(uuid=ticket_data['source'])
                if not source:
                    source_node_data = NodesAPI(node.uri()).get(
                            Node.absolute_url(source))
                    source = Node.from_dict(source_node_data)
                return Ticket(stream=stream, source=source,
                        source_port=ticket_data['source_port'],
                        destination=destination,
                        hops=ticket_data['hops'] + 1)

    @classmethod
    def _request_stream_from_watchers(cls, stream, destination,
            unconfirmed_tickets=None):
        tickets = []
        for ticket in Ticket.query.filter_by(stream=stream):
            if cls._already_seeding(ticket):
                return [ticket]
            else:
                if not cls._already_ticketed(unconfirmed_tickets,
                        ticket.destination):
                    tickets.append(cls._request_stream_from_node(stream,
                            ticket.destination, destination=destination))
        return filter(None, tickets)

    @classmethod
    def _request_stream_from_supernodes(cls, stream, destination,
            unconfirmed_tickets=None):
        tickets = []
        for supernode in Node.supernodes():
            if supernode != Node.me() and not cls._already_ticketed(
                    unconfirmed_tickets, destination):
                tickets.append(cls._request_stream_from_node(stream,
                    supernode, destination))
        return filter(None, tickets)

    @classmethod
    def _request_stream_from_source(cls, stream, destination,
            unconfirmed_tickets=None):
        log.info("Requesting %s from the source, %s, to be delivered to %s",
                stream, stream.source, destination)
        return [cls._request_stream_from_node(stream, stream.source,
            destination)]

    @classmethod
    def _request_stream(cls, stream, destination):
        unconfirmed_tickets = []
        for possible_source_method in [cls._request_stream_from_source,
                cls._request_stream_from_supernodes,
                cls._request_stream_from_watchers]:
            unconfirmed_tickets.extend(possible_source_method(stream,
                destination, unconfirmed_tickets=unconfirmed_tickets))
        return filter(None, unconfirmed_tickets)

    @classmethod
    def _request_stream_from_others(cls, stream, destination):
            unconfirmed_tickets = cls._request_stream(stream, destination)
            if not unconfirmed_tickets:
                raise HTTPError(412)
            unconfirmed_tickets = set(unconfirmed_tickets)
            bad_tickets = set()
            for ticket in unconfirmed_tickets:
                ticket.source.update_rtt()
                if Node.me().supernode and not ticket.source.rtt:
                    log.info("Informing web server that %s is unresponsive "
                            "and should be deleted", ticket.source)
                    NodesAPI(settings.ASTRAL_WEBSERVER).unregister(
                            ticket.source.absolute_url())
                    bad_tickets.append(ticket)
            unconfirmed_tickets = unconfirmed_tickets - bad_tickets
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
            return closest

    @classmethod
    def handle_ticket_request(cls, stream, destination):
        log.debug("Trying to create a ticket to serve %s to %s",
                stream, destination)
        new_ticket = cls._already_streaming(stream, destination)
        if new_ticket:
            log.info("%s already has a ticket for %s (%s) -- refreshing with "
                    "destination to be sure", destination, stream, new_ticket)
            existing_ticket = cls._request_stream_from_node(stream,
                    new_ticket.source, destination)
            if existing_ticket:
                existing_ticket.refreshed = datetime.datetime.now()
                # In case we lost the tunnel, just make sure it exists
                existing_ticket.queue_tunnel_creation()
                session.commit()
                return existing_ticket
            log.info("%s didn't confirm our old ticket %s, must get a new "
                    "one", new_ticket.source, new_ticket)

        if stream.source != Node.me():
            new_ticket = cls._offer_ourselves(stream, destination)
            if new_ticket:
                log.info("We can stream %s to %s, created %s",
                    stream, destination, new_ticket)
                # In case we lost the tunnel, just make sure it exists
                new_ticket.queue_tunnel_creation()
            elif Node.me().supernode or destination == Node.me():
                log.info("Propagating the request for streaming %s to %s to "
                        "our other known nodes", stream, destination)
                new_ticket = cls._request_stream_from_others(stream,
                        destination)
            else:
                raise HTTPError(412)
        else:
            new_ticket = Ticket(stream=stream, destination=destination)
            log.info("%s is the source of %s, created %s", destination,
                    stream, new_ticket)
        session.commit()
        return new_ticket

    def post(self, stream_slug):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        stream = Stream.get_by(slug=stream_slug)
        if not stream:
            try:
                log.debug("Don't know of stream with slug %s, asking the "
                        "origin", stream_slug)
                stream_data = StreamsAPI(settings.ASTRAL_WEBSERVER).find(
                        stream_slug)
            except NetworkError, e:
                log.warning("Can't connect to server: %s", e)
            except NotFound:
                log.debug("Origin didn't know of a stream with slug",
                        stream_slug)
                raise HTTPError(404)
            else:
                stream = Stream.from_dict(stream_data)
        if not stream:
            log.debug("Couldnt find stream with slug %s anywhere", stream_slug)
            raise HTTPError(404)
        destination_uuid = self.get_json_argument('destination_uuid', '')
        if destination_uuid:
            destination = Node.get_by(uuid=destination_uuid)
            # TODO since we only have the IP, we have to assume the port is 8000
            # to be able to request back to it for more details. hmm.
            # TODO another problem is that the tornado server is (and i should
            # have realized this sooner...) single-threaded, and based on the
            # event model. So the requsting node is blocked waiting for us to
            # responsed, then we go and query it. well, that's deadlock! a
            # workaroud since we're only dealing with single supernode
            # situations is just to query the supernode, since they MUST know
            # about that other node.
            if not destination:
                try:
                    log.debug("Don't know of a node with UUID %s for the "
                            "ticket destination -- asking the requester at "
                            "http://%s:%s", destination_uuid,
                            self.request.remote_ip, settings.PORT)
                    # TODO here in the future we would change it to the
                    # remote_ip. now just does supernode.
                    from ipdb import set_trace; set_trace(); # TODO
                    node_data = NodesAPI(Node.me().primary_supernode.uri()
                            ).find(destination_uuid)
                except NetworkError, e:
                    log.warning("Can't connect to server: %s", e)
                except NotFound:
                    log.debug("Request didn't know of a node with UUID",
                            destination_uuid)
                    raise HTTPError(404)
                else:
                    destination = Node.from_dict(node_data)
            if not destination:
                log.debug("Couldnt find node with UUID %s anywhere",
                        destination_uuid)
                raise HTTPError(404)
        else:
            destination = Node.me()

        new_ticket = self.handle_ticket_request(stream, destination)
        self.redirect(new_ticket.absolute_url())

    def get(self):
        """Return a JSON list of all known tickets."""
        self.write({'tickets': [ticket.to_dict()
                for ticket in Ticket.query.all()]})
