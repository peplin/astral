
from tornado.web import HTTPError

from astral.api.handlers.base import BaseHandler
from astral.models import Ticket, Node, Stream, session

import logging
logger = logging.getLogger(__name__)


class TicketsHandler(BaseHandler):
    def post(self, stream_id):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        stream = Stream.get_by(id=stream_id)
        destination_uuid = self.get_json_argument('destination_uuid', '')
        if destination_uuid:
            # TODO observe some cap on the number of tickets, based on bandwidth
            node = Node.get_by(uuid=destination_uuid)
            if not node:
                raise HTTPError(404)
            Ticket(stream=stream, source=Node.me(), destination=node)
        else:
            # TODO See LH #35
            Ticket(stream=stream, source=Node.me(), destination=Node.me())
        session.commit()
        self.redirect(stream.absolute_url())
