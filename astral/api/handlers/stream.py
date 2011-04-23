from tornado import web

from astral.api.handlers.base import BaseHandler
from astral.models import Stream

import logging
log = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def get(self, stream_slug):
        """Return metadata for the stream."""
        # TODO accept edits to the 'streaming' attribute through GET, which
        # while not ideal, is the easiest way to get around the same-origin
        # policy in the browser.
        stream = Stream.get_by(slug=stream_slug)
        if not stream:
            raise web.HTTPError(404)
        if 'streaming' in self.request.arguments:
            stream.streaming = self.request.arguments['streaming'][0] == 'true'
        self.write({'stream': stream.to_dict()})

    def put(self, stream_slug):
        stream = Stream.get_by(slug=stream_slug)
        if stream:
            stream.streaming = self.get_json_argument('streaming')
            if stream.streaming:
                log.info("Resumed streaming %s", stream)
            else:
                log.info("Paused streaming %s", stream)
