from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def post(self):
        """Return whether or not this node can forward the stream requested to
        the requesting node, and start doing so if it can."""
        # TODO

    def get(self):
        """Return metadata for the stream."""
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
        # TODO if this GET is metadata, what's the endpoint for the actual
        # stream? Does it come through a different socket, outside of torando?

    def delete(self):
        """Stop forwarding the stream to the requesting node."""
        # TODO
