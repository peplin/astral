from tornado.web import HTTPError

from astral.api.handlers.base import BaseHandler
from astral.models import Ticket, Node, Stream, session

import logging
logger = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def post(self, stream_id):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        # TODO See LH #35
        # TODO observe some cap on the number of tickets, based on bandwidth
        stream = Stream.get_by(id=stream_id)
        node = Node.get_by(ip_address=self.request.remote_ip)
        if not node:
            raise HTTPError(404)
        Ticket(stream=stream, node=node)
        session.commit()
        self.get(stream_id)

    def get(self, stream_id):
        """Return metadata for the stream."""
        self.write({'stream': Stream.get_by(id=stream_id).to_dict()})
        # TODO could require target nodes to hit this every so often as a
        # heartbeat

    def delete(self, stream_id):
        """Stop forwarding the stream to the requesting node."""
        node = Node.get_by(ip_address=self.request.remote_ip)
        if node:
            ticket = Ticket.get_by(stream_id=stream_id, node=node)
            if ticket:
                ticket.delete()
