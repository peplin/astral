from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class StreamHandler(BaseHandler):
    def get(self):
        self.write({})
