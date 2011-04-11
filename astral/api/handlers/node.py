from astral.api.handlers.base import BaseHandler
from astral.models.node import Node
from astral.api.client import NodesAPI
import sys


import logging
log = logging.getLogger(__name__)


class NodeHandler(BaseHandler):
    def delete(self, node_uuid=None):
        """Remove the requesting node from the list of known nodes,
        unregistering the from the network.
        """

        print "***Entered Handler"
        if node_uuid:
            node = Node.get_by(uuid=node_uuid)
        else:
            print "Node is me@@@@@"
            node = Node.me()
            temp = node
            print "common!!!", node, temp, Node.me()
        node.delete()

        print "after deletion", node , temp, Node.me()

        if node_uuid:
            node = Node.get_by(uuid=node_uuid)
        else:
            node = Node.me()
        node.delete()


        closest_supernode = Node.closest_supernode()
        if closest_supernode:
            log.info("Notifying closest supernode %s that %s was deleted",
                    closest_supernode, node)
            NodesAPI(closest_supernode.absolute_url()).unregister(node)

        print "before last if********", node , temp, Node.me()
        sys.exit()

        if temp == Node.me():
            # TODO kind of a shortcut to shutting down, but should be a bit more
            # formal
            print "Entering if********"
            GenerateConsoleCtrlEvent(CTRL_C_EVENT, 0) 
            """shut = Daemon()
            shut.stop()
            raise KeyboardInterrupt"""


        if node == Node.me():
            # TODO kind of a shortcut to shutting down, but should be a bit more
            # formal
            raise KeyboardInterrupt
