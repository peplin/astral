import json

from astral.api.handlers.base import BaseHandler
from astral.models import Ticket, Node, Stream

import logging
logger = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def post(self, stream_id):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        # TODO

    def get(self, stream_id):
        """Return metadata for the stream."""
        self.write(json.dumps({'stream': Stream.get_by(id=stream_id).to_dict()}))
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
        # TODO if this GET is metadata, what's the endpoint for the actual
        # stream? Does it come through a different socket, outside of torando?

    def delete(self, stream_id):
        """Stop forwarding the stream to the requesting node."""
        node = Node.get_by(ip_address=self.request.remote_ip)
        if node:
            ticket = Ticket.get_by(stream_id=stream_id, node=node)
            if ticket:
                ticket.delete()
