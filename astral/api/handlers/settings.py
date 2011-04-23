from astral.api.handlers.base import BaseHandler
from astral.conf import settings

import logging
log = logging.getLogger(__name__)


class PingHandler(BaseHandler):
    def get(self):
        """Return settings like port numbers and URL endpoints so other the
        browser and Flash player can determine these dynamically.
        """
        self.write({'rtmp_port': settings.RTMP_PORT,
            'rtmp_resource': settings.RTMP_APP_NAME,
            'rtmp_tunnel_port': settings.RTMP_TUNNEL_PORT})
