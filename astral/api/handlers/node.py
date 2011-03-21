from astral.api.handlers.base import BaseHandler
from astral.models.node import Node

import logging
logger = logging.getLogger(__name__)


class NodeHandler(BaseHandler):
    def delete(self, uuid):
        """Remove the requesting node from the list of known nodes,
        unregistering the from the network.
        """
        Node.get_by(uuid=uuid).delete()
        # TODO consider forwarding this data to other known nodes
