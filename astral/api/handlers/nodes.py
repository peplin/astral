import json

from astral.api.handlers.base import BaseHandler
from astral.models.node import Node

import logging
logger = logging.getLogger(__name__)


class NodesHandler(BaseHandler):
    def get(self):
        """Return a JSON list of all known nodes, with metadata."""
        self.write(json.dumps({'nodes': [node.to_dict()
            for node in Node.query.all()]}))

    def post(self):
        """Add the node specified in POSTed JSON to the list of known nodes."""
        # TODO
