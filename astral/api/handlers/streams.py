from astral.conf import settings
from astral.api.handlers.base import BaseHandler
from astral.api.client import StreamsAPI
from astral.models import Stream, Node
from astral.exceptions import NetworkError

import logging
log = logging.getLogger(__name__)


class StreamsHandler(BaseHandler):
    def get(self):
        """Return a JSON list of streams that this node can forward."""
        self.write({'streams': [stream.to_dict()
                for stream in Stream.query.all()]})

    def post(self):
        """Register a new available stream."""
        self.get_json_argument('name')
        self.request.arguments['source'] = Node.me()
        stream = Stream.from_dict(self.request.arguments)
        try:
            StreamsAPI(settings.ASTRAL_WEBSERVER).create(
                    source_uuid=stream.source.uuid, name=stream.name,
                    description=stream.description)
        except NetworkError, e:
            log.warning("Unable to register stream with origin webserver: %s",
                    e)
