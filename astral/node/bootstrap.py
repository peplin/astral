import threading
from restkit import RequestFailed


from astral.models import Node, session, Stream
from astral.exceptions import RequestError
from astral.node.upstream import UpstreamCheckThread
from astral.conf import settings
from astral.api.client import NodesAPI, StreamsAPI

import logging
log = logging.getLogger(__name__)


class BootstrapThread(threading.Thread):
    """Runs once at node startup to build knowledge of the network."""

    def __init__(self, node, upstream_limit):
        super(BootstrapThread, self).__init__()
        self.node = node
        self.upstream_limit = upstream_limit

    def load_static_bootstrap_nodes(self):
        log.info("Loading static bootstrap nodes %s",
                settings.BOOTSTRAP_NODES)
        nodes = [Node.from_dict(node) for node in settings.BOOTSTRAP_NODES]
        session.commit()
        log.debug("Loaded static bootstrap nodes %s", nodes)

    def load_dynamic_bootstrap_nodes(self, base_url=None):
        base_url = base_url or settings.ASTRAL_WEBSERVER
        try:
            nodes = NodesAPI(base_url).list()
        except RequestError, e:
            log.warning("Can't connect to server: %s", e)
        else:
            log.debug("Nodes returned from the server: %s", nodes)
            for node in nodes:
                if self.node().conflicts_with(node):
                    log.warn("Received %s which conflicts with us (%s) "
                            "-- telling web server to kill it",
                            node, self.node())
                    NodesAPI(base_url).unregister(self.node().absolute_url())
                else:
                    node = Node.from_dict(node)
                    log.info("Stored %s from %s", node, base_url)

    def load_streams(self, base_url=None):
        base_url = base_url or settings.ASTRAL_WEBSERVER
        try:
            streams = StreamsAPI(base_url).list()
        except RequestError, e:
            log.warning("Can't connect to server: %s", e)
        else:
            log.debug("Streams returned from the server: %s", streams)
            for stream in streams:
                stream = Stream.from_dict(stream)
                if stream:
                    log.info("Stored %s from %s", stream, base_url)
        self.prime_stream_tunnels()

    def prime_stream_tunnels(self):
        for stream in Stream.query.filter(Stream.source == Node.me()):
            stream.queue_tunnel_status_flip()

    def register_with_origin(self):
        try:
            NodesAPI(settings.ASTRAL_WEBSERVER).register(
                    self.node().to_dict())
        except RequestError, e:
            log.warning("Can't connect to server to register as a "
                    "supernode: %s", e)

    def register_with_supernode(self):
        Node.update_supernode_rtt()
        # TODO hacky hacky hacky. moving query inside of the node causes
        # SQLAlchemy session errors.
        session.commit()
        session.close_all()

        if not self.node().supernode:
            if not Node.supernodes():
                self.node().supernode = True
                log.info("Registering %s as a supernode, none others found",
                        self.node())
                self.register_with_origin()
            else:
                for supernode in Node.supernodes().order_by('rtt'):
                    self.node().primary_supernode = supernode
                    try:
                        NodesAPI(self.node().primary_supernode.uri()).register(
                                self.node().to_dict())
                    except RequestError, e:
                        log.warning("Can't connect to supernode %s to register"
                                ": %s", self.node().primary_supernode, e)
                        log.info("Informing web server that supernode %s is "
                                "unresponsive and should be deleted", supernode)
                        NodesAPI(settings.ASTRAL_WEBSERVER).unregister(
                                supernode.absolute_url())
                        self.node().primary_supernode = None
                    except RequestFailed, e:
                        log.warning("%s rejected us as a child node: %s",
                                supernode, e)
                        self.node().primary_supernode = None
                    else:
                        self.load_dynamic_bootstrap_nodes(
                                self.node().primary_supernode.uri())
                if not self.node().primary_supernode:
                    self.node().supernode = True
                    log.info("No supernode could take us - "
                            "registering ourselves %s as a supernode",
                            self.node())
                    self.register_with_origin()
        else:
            log.info("Registering %s as a supernode, my database told me so",
                    self.node())
            self.register_with_origin()
            for supernode in Node.supernodes():
                if supernode != Node.me():
                    try:
                        NodesAPI(supernode.uri()).register(
                                self.node().to_dict())
                    except RequestError, e:
                        log.warning("Can't connect to supernode %s: %s",
                                supernode, e)
                        supernode.delete()
                        log.info("Informing web server that %s is unresponsive "
                                "and should be deleted", supernode)
                        NodesAPI(settings.ASTRAL_WEBSERVER).unregister(
                                supernode.absolute_url())
                    except RequestFailed:
                        log.warning("%s threw an error - sure it's not "
                                "running on another computer in your LAN with "
                                "the same remote IP?", supernode)
                        supernode.delete()
        session.commit()

    def run(self):
        UpstreamCheckThread(self.node, self.upstream_limit).run()
        Node.me(refresh=True)
        self.load_static_bootstrap_nodes()
        self.load_dynamic_bootstrap_nodes()
        self.register_with_supernode()
        self.load_streams()
        session.commit()
