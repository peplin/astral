from tornado.web import HTTPError

from astral.conf import settings
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
        if (Node.me().supernode and self.get_json_argument(
                    'primary_supernode_uuid', '') == Node.me().uuid):
            children_count = Node.query.filter_by(primary_supernode=Node.me()
                    ).count()
            if children_count > settings.SUPERNODE_MAX_CHILDREN:
                raise HTTPError(503)
        if not Node.get_by(uuid=uuid):
            # TODO what if supernode changes? need to update
            self.request.arguments.setdefault('ip_address',
                    self.request.remote_ip)
            Node.from_dict(self.request.arguments)
            session.commit()
