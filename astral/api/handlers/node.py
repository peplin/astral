from astral.api.handlers.base import BaseHandler
from astral.models.node import Node
from astral.api.client import NodesAPI

import logging
log = logging.getLogger(__name__)


class NodeHandler(BaseHandler):
    def delete(self, uuid):
        """Remove the requesting node from the list of known nodes,
        unregistering the from the network.
        """
        node = Node.get_by(uuid=uuid)
        node.delete()
        closest_supernode = Node.closest_supernode()
        if closest_supernode:
            log.info("Notifying closest supernode %s that %s was deleted",
                    closest_supernode, node)
            NodesAPI(closest_supernode.absolute_url()).delete(node)
