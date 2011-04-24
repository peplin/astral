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
        self.agent = rtmp.FlashServer()
        self.agent.apps = dict({settings.RTMP_APP_NAME: self.AstralApp})

    def run(self):
        # TODO this doesn't give up its port when the node autoreloads the code,
        # so this thread dies. How can we make it properly shut down?
        log.info("Starting RTMP server on port %d", settings.RTMP_PORT)
        self.agent.start('0.0.0.0', settings.RTMP_PORT)
        multitask.run()

    def stop(self):
        log.info("Stopping the RTMP server on port %d", settings.RTMP_PORT)
        self.agent.stop()

    # TO DO: overwrite Protocol.parsemessage to intercept and forward data
    # packets between Astral nodes (start-up messages will need to be simulated)
    class AstralApp(rtmp.App):
        def __init__(self):
            rtmp.App.__init__(self)
