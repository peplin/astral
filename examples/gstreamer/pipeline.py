#!/usr/bin/env python

import pygst
pygst.require("0.10")
import gst
import gtk


class Pipeline(object):
    def __init__(self):
        self.pipeline = gst.Pipeline("pipe")
        self.audio_source = gst.element_factory_make("audiotestsrc", "audio")
        self.audio_source.set_property("freq", 2000)
        self.pipeline.add(self.audio_source)

        self.sink = gst.element_factory_make("alsasink", "sink")
        self.pipeline.add(self.sink)

        self.audio_source.link(self.sink)
        self.pipeline.set_state(gst.STATE_PLAYING)

start = Pipeline()
gtk.main()
