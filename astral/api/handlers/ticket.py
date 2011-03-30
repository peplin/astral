from astral.api.handlers.base import BaseHandler
from astral.models import Ticket, Node

import logging
logger = logging.getLogger(__name__)


class TicketHandler(BaseHandler):
    def delete(self, stream_id, destination_uuid=None):
        """Stop forwarding the stream to the requesting node."""
        if destination_uuid:
            node = Node.get_by(uuid=destination_uuid)
        else:
            node = Node.me()

        if node:
            ticket = Ticket.get_by(stream_id=stream_id, destination=node)
            if ticket:
                ticket.delete()

    def get(self, stream_id):
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
        pass
