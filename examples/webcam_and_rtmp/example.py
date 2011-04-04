#! /usr/bin/env python

import rtmp, multitask


# TO DO: overwrite Protocol.parsemessage to intercept and forward data packets between Astral nodes (start-up messages will need to be simulated)
class AstralApp(rtmp.App):                                  # AstralApp extends the default App in rtmp module.
    def __init__(self):                                     # constructor invokes base class constructor
        rtmp.App.__init__(self)


# rtmp://localhost:1935/astral receives and forwards streams
rtmp._debug = True
agent = rtmp.FlashServer()                                  # a new RTMP server instance
agent.apps = dict({'astral': AstralApp})                    # rtmp://ADDR:PORT/astral will route to our AstralApp instance
agent.start('0.0.0.0', 1935)                                # start the server on localhost port 1935
multitask.run()