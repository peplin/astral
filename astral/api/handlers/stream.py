from astral.api.handlers.base import BaseHandler
from astral.models import Stream

import logging
logger = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def get(self, stream_id):
        """Return metadata for the stream."""
        self.write({'stream': Stream.get_by(id=stream_id).to_dict()})
        # TODO could require target nodes to hit this every so often as a
        # heartbeat
