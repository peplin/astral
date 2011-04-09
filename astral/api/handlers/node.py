from astral.api.handlers.base import BaseHandler
from astral.models.node import Node
from astral.api.client import NodesAPI

import logging
log = logging.getLogger(__name__)


class NodeHandler(BaseHandler):
    def delete(self, node_uuid=None):
        """Remove the requesting node from the list of known nodes,
        unregistering the from the network.
        """
        if node_uuid:
            node = Node.get_by(uuid=node_uuid)
        else:
            node = Node.me()
        node.delete()

        closest_supernode = Node.closest_supernode()
        if closest_supernode:
            log.info("Notifying closest supernode %s that %s was deleted",
                    closest_supernode, node)
            NodesAPI(closest_supernode.absolute_url()).delete(node)

        if node == Node.me():
            # TODO kind of a shortcut to shutting down, but should be a bit more
            # formal
            raise KeyboardInterrupt
