import tornado.ioloop, tornado.web

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

        if not node_uuid or node_uuid == Node.me().uuid:
            log.info("Shutting down because of request from %s",
                    self.request.remote_ip)
            tornado.ioloop.IOLoop.instance().stop()
            return

        node = Node.get_by(uuid=node_uuid)
        if node:
            closest_supernode = Node.closest_supernode()
            if closest_supernode and node != closest_supernode:
                log.info("Notifying closest supernode %s that %s was deleted",
                        closest_supernode, node)
                NodesAPI(closest_supernode.absolute_url()).unregister(node)
            if node == Node.me().primary_supernode:
                # [LH #151] this should work, but there should be a more direct way
                # to re-do the supernode registration. maybe move the
                # register_with_supernode method to the Node model.
                from astral.node.bootstrap import BootstrapThread
                BootstrapThread(node=Node.me, upstream_limit=None).start()
            node.delete()

    def get(self, node_uuid=None):
        if not node_uuid:
            node = Node.get_by(uuid=Node.me().uuid)
        else:
            node = Node.get_by(uuid=node_uuid)
        if not node:
            raise tornado.web.HTTPError(404)
        self.write({'node': node.to_dict()})
