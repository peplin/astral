from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class StreamsHandler(BaseHandler):
    def get(self):
        self.write({})
