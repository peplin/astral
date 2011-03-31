from astral.api.handlers.base import BaseHandler
from astral.conf import settings

import logging
log = logging.getLogger(__name__)


class PingHandler(BaseHandler):
    def get(self):
        """If 'bytes' is specified in the query string, return that number of
        random bytes (for the purposes of a downstream bandwidth measurement).
        Otherwise, returns a simple 200 OK HTTP response, to check the RTT.
        """
        byte_count = self.get_argument('bytes', None)
        if byte_count:
            byte_count = int(byte_count)
            log.debug("Returning %s bytes for a downstream bandwidth test",
                    byte_count)
            with open('/dev/urandom') as random_file:
                self.write({'data': random_file.read(
                    max(byte_count, settings.DOWNSTREAM_CHECK_LIMIT))})
        else:
            self.write({'result': "Pong!"})
            log.debug("Responded to a ping")

    def post(self):
        """Accept arbitrary POST data to check upstream bandwidth. Limit the
        size to make sure we aren't DoS'd.
        """
        log.debug("Received an upstream bandwidth check with %s bytes",
                len(self.request.body))
