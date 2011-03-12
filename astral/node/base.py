"""
astral.node.base
==========

Node Base Class.

"""
import astral.api
import astral.models

class Node(object):
    def __init__(self):
        pass

    def run(self, **kwargs):
        astral.api.run()
