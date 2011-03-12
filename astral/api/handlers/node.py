from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class NodeHandler(BaseHandler):
    def delete(self):
        """Remove the requesting node from the list of known nodes,
        unregistering the from the network.
        """
        # TODO
        # TODO consider forwarding this data to other known nodes
