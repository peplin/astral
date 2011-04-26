from astral.api.handlers.base import BaseHandler
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
        if ticket:
            ticket.delete()
        # TODO if we were the destination, need to find another ticket
        # TODO if we were forwarding this to someone else, need to propagate the
        # delete to them if we can't find another

    def get(self, stream_slug, destination_uuid=None):
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
        ticket = self._load_ticket(stream_slug, destination_uuid)
        if ticket:
            # In case we lost the tunnel, just make sure it exists
            ticket.queue_tunnel_creation()
            # TODO this is unideal, but we need to get the new port if it
            # changed. combination of sleep and db flush seems to do it somewhat
            # reliably, but it's still a race condition.
            import time
            time.sleep(1)
            session.commit()
            ticket = self._load_ticket(stream_slug, destination_uuid)
            self.write({'ticket': ticket.to_dict()})

    def put(self, stream_slug, destination_uuid=None):
        """Edit tickets, most likely just confirming them."""
        ticket = self._load_ticket(stream_slug, destination_uuid)
        if ticket:
            ticket.confirmed = self.get_json_argument('confirmed')
            if ticket.confirmed:
                log.info("Confirmed %s", ticket)
