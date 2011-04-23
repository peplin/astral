import threading

from astral.conf import settings
from astral.rtmp import rtmp, multitask

import logging
log = logging.getLogger(__name__)


class StreamingThread(threading.Thread):
    """Manages the RTMP server and socket forwarder.
    The server is exposed at localhost:RTMP_PORT/RTMP_APP_NAME.
    """

    def __init__(self):
        super(StreamingThread, self).__init__()
        self.daemon = True

    def run(self):
        rtmp._debug = settings.DEBUG
        agent = rtmp.FlashServer()
        agent.apps = dict({settings.RTMP_APP_NAME: self.AstralApp})
        agent.start('0.0.0.0', settings.RTMP_PORT)
        multitask.run()

    # TO DO: overwrite Protocol.parsemessage to intercept and forward data
    # packets between Astral nodes (start-up messages will need to be simulated)
    class AstralApp(rtmp.App):
        def __init__(self):
            rtmp.App.__init__(self)
