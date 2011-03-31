from astral.api.handlers.base import BaseHandler
from astral.models import Node, session

import logging
logger = logging.getLogger(__name__)


class NodesHandler(BaseHandler):
    def get(self):
        """Return a JSON list of all known nodes, with metadata."""
        self.write({'nodes': [node.to_dict() for node in Node.query.all()]})

    def post(self):
        """Add the node specified in POSTed JSON to the list of known nodes."""
        uuid = self.get_json_argument('uuid')
        if not Node.get_by(uuid=uuid):
            self.request.arguments['ip_address'] = self.request.remote_ip
            Node.from_dict(self.request.arguments)
            session.commit()
