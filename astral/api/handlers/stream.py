from tornado import web

from astral.api.handlers.base import BaseHandler
from astral.models import Stream

import logging
log = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def get(self, stream_slug):
        """Return metadata for the stream."""
        stream = Stream.get_by(slug=stream_slug)
        if not stream:
            raise web.HTTPError(404)
        self.write({'stream': stream.to_dict()})

    def put(self, stream_slug):
        stream = Stream.get_by(slug=stream_slug)
        if stream:
            # this accepts the streaming flag as a query parameter to get around
            # the same-origin policy, as we can't get PUT data from the browser.
            if 'streaming' in self.request.arguments:
                stream.streaming = self.request.arguments['streaming']
            else:
                stream.streaming = self.get_json_argument('streaming')
            if stream.streaming:
                log.info("Resumed streaming %s", stream)
            else:
                log.info("Paused streaming %s", stream)
