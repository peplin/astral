from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class NodesHandler(BaseHandler):
    def get(self):
        """Return a JSON list of all known nodes, with metadata."""
        # TODO
        self.write({})

    def post(self):
        """Add the node specified in POSTed JSON to the list of known nodes."""
        # TODO
