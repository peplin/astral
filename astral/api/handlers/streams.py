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
        # TODO kind of messy way to handle two different data types, but for
        # some reason Torando is loading the name and description as lists
        # instead of strings if they are form encded
        if not hasattr(self.request, 'arguments') or not self.request.arguments:
            self.load_json()
        else:
            self.request.arguments['name'] = self.request.arguments['name'][0]
            self.request.arguments['description'] = (
                    self.request.arguments['description'][0])

        self.request.arguments['source'] = Node.me()
        stream = Stream.from_dict(self.request.arguments)
        try:
            StreamsAPI(settings.ASTRAL_WEBSERVER).create(
                    source_uuid=stream.source.uuid, name=stream.name,
                    slug=stream.slug, description=stream.description)
        except NetworkError, e:
            log.warning("Unable to register stream with origin webserver: %s",
                    e)
            # TODO we do this a second time here because sometimes the first one
            # fails, but it never seems to actually attempt to make the request
            # - sinatra shows nothing in the logs. it's difficult to debug
            # because it's so intermittent.
            StreamsAPI(settings.ASTRAL_WEBSERVER).create(
                    source_uuid=stream.source.uuid, name=stream.name,
                    slug=stream.slug, description=stream.description)
        self.redirect("%s/stream/%s"
                % (settings.ASTRAL_WEBSERVER, stream.slug))
