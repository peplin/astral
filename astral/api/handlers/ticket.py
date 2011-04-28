from tornado.web import HTTPError
import datetime

from astral.api.client import TicketsAPI
from astral.api.handlers.base import BaseHandler
from astral.api.handlers.tickets import TicketsHandler
from astral.models import Ticket, Node, Stream, session

import logging
log = logging.getLogger(__name__)


class TicketHandler(BaseHandler):
    def _load_ticket(self, stream_slug, destination_uuid):
        stream = Stream.get_by(slug=stream_slug)
        if not destination_uuid:
            return Ticket.get_by(stream=stream, destination=Node.me())

        node = Node.get_by(uuid=destination_uuid)
        return Ticket.query.filter_by(stream=stream, destination=node).first()

    def delete(self, stream_slug, destination_uuid=None):
        """Stop forwarding the stream to the requesting node."""
        ticket = self._load_ticket(stream_slug, destination_uuid)
        if not ticket:
            raise HTTPError(404)

        if ticket.confirmed and not ticket.source == Node.me():
            if ticket.destination == Node.me():
                if self.request.remote_ip == '127.0.0.1':
                    log.info("User is canceling %s -- must inform sender",
                            ticket)
                    TicketsAPI(ticket.source.uri()).cancel(
                            ticket.absolute_url())
                else:
                    log.info("%s is being deleted, we need to find another for "
                            "ourselves", ticket)
                    try:
                        TicketsHandler.handle_ticket_request(ticket.stream,
                                ticket.destination)
                    except HTTPError, e:
                        log.warning("We lost %s and couldn't find a "
                                "replacement to failover -- our stream is "
                                "dead: %s", ticket, e)
            elif self.request.remote_ip == ticket.source.ip_address:
                log.info("%s is being deleted by the source, must inform the "
                        "target %s", ticket, ticket.destination)
                TicketsAPI(ticket.destination.uri()).cancel(
                        ticket.absolute_url())
            elif self.request.remote_ip == ticket.destination.ip_address:
                log.info("%s is being deleted by the destination, must inform "
                        "the source %s", ticket, ticket.source)
                TicketsAPI(ticket.source.uri()).cancel(ticket.absolute_url())
        if ticket:
            ticket.delete()
            session.commit()

    def get(self, stream_slug, destination_uuid=None):
        ticket = self._load_ticket(stream_slug, destination_uuid)
        if ticket:
            # TODO this block is somewhat duplicated from TicketsHandler.post,
            # where we refresh an existing ticket.
            log.info("Refreshing %s with the source", ticket)
            ticket = TicketsHandler._request_stream_from_node(ticket.stream,
                    ticket.source, ticket.destination, existing_ticket=ticket)
            if ticket:
                ticket.refreshed = datetime.datetime.now()
                # In case we lost the tunnel, just make sure it exists
                ticket.queue_tunnel_creation()
                session.commit()
                # TODO this is unideal, but we need to get the new port if it
                # changed. combination of sleep and db flush seems to do it
                # somewhat reliably, but it's still a race condition.
                import time
                time.sleep(1)
            ticket = self._load_ticket(stream_slug, destination_uuid)
            self.write({'ticket': ticket.to_dict()})

    def put(self, stream_slug, destination_uuid=None):
        """Edit tickets, most likely just confirming them."""
        ticket = self._load_ticket(stream_slug, destination_uuid)
        if ticket:
            ticket.confirmed = self.get_json_argument('confirmed')
            if ticket.confirmed:
                log.info("Confirmed %s", ticket)
            session.commit()
