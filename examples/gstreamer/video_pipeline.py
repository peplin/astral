#!/usr/bin/env python

import pygst
pygst.require("0.10")
import gst
import gtk


class Pipeline(object):
    def __init__(self):
        self.pipeline = gst.Pipeline("pipe")
        self.webcam = gst.element_factory_make("v4l2src", "webcam")
        self.webcam.set_property("device", "/dev/video0")
        self.pipeline.add(self.webcam)
        self.caps_filter = gst.element_factory_make("capsfilter", "caps_filter")
        caps = gst.Caps("video/x-raw-yuv,width=640,height=480,framerate=30/1")
        self.caps_filter.set_property("caps", caps)
        self.pipeline.add(self.caps_filter)

        self.sink = gst.element_factory_make("xvimagesink", "sink")
        self.pipeline.add(self.sink)

        self.webcam.link(self.caps_filter)
        self.caps_filter.link(self.sink)
        self.pipeline.set_state(gst.STATE_PLAYING)

start = Pipeline()
gtk.main()
