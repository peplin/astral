from astral.api.handlers.base import BaseHandler
from astral.conf import settings

import logging
logger = logging.getLogger(__name__)


class PingHandler(BaseHandler):
    def get(self):
        """If 'bytes' is specified in the query string, return that number of
        random bytes (for the purposes of a downstream bandwidth measurement).
        Otherwise, returns a simple 200 OK HTTP response, to check the RTT.
        """
        byte_count = self.get_argument('bytes')
        if byte_count:
            with open('/dev/random') as random_file:
                self.write(random_file.read(
                    max(byte_count, settings.BANDWIDTH_CHECK_SIZE_LIMIT)))
