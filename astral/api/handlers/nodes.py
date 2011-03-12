from astral.api.handlers.base import BaseHandler

import logging
logger = logging.getLogger(__name__)


class NodesHandler(BaseHandler):
    def get(self):
        self.write({})
