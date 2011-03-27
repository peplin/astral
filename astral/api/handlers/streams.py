
from astral.api.handlers.base import BaseHandler
from astral.models.stream import Stream

import logging
logger = logging.getLogger(__name__)


class StreamsHandler(BaseHandler):
    def get(self):
        """Return a JSON list of streams that this node can forward."""
        self.write({'streams': [stream.to_dict()
                for stream in Stream.query.all()]})

    def post(self):
        """Register a new available stream."""
        # TODO this might be not neccessary, if everyone goes back to the www
        # server to get the list of streams. another way it could work is that
        # the web server pushes out new stream notifications to supernodes, and
        # other nodes just ask the supernodes. the activity is triggered by user
        # typing in a name in the command line or clicking on a link in the
        # browser, so the request from that client could just be propagated back
        # to a node that has heard of it. hmm. needs some thought.
