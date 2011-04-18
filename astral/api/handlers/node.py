import tornado.ioloop

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

        if not node_uuid:
            log.info("Shutting down because of request from %s",
                    self.request.remote_ip)
            tornado.ioloop.IOLoop.instance().stop()
            return

        node = Node.get_by(uuid=node_uuid)
        closest_supernode = Node.closest_supernode()
        if closest_supernode:
            log.info("Notifying closest supernode %s that %s was deleted",
                    closest_supernode, node)
            NodesAPI(closest_supernode.absolute_url()).unregister(node)
        node.delete()
