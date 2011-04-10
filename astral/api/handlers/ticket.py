from astral.api.handlers.base import BaseHandler
from astral.models import Ticket, Node

import logging
logger = logging.getLogger(__name__)


class TicketHandler(BaseHandler):
    def _load_ticket(self, stream_id, destination_uuid):
        if not destination_uuid:
            return Ticket.get_by(stream_id=stream_id, source=Node.me(),
                    destination=Node.me())

        node = Node.get_by(uuid=destination_uuid)
        query = Ticket.query.filter_by(stream_id=stream_id).filter_by(
                destination=node)
        if node == Node.me():
                    query.filter(Ticket.source != Node.me())
        return query.first()

    def delete(self, stream_id, destination_uuid=None):
        """Stop forwarding the stream to the requesting node."""
        ticket = self._load_ticket(stream_id, destination_uuid)
        if ticket:
            ticket.delete()

    def get(self, stream_id, destination_uuid=None):
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
        ticket = self._load_ticket(stream_id, destination_uuid)
        if ticket:
            self.write({'ticket': ticket.to_dict()})
