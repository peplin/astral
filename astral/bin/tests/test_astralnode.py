import unittest2 

from astral.bin.astralnode import NodeCommand

class NodeCommandTest(unittest2.TestCase):
    def test_basic_run(self):
        cmd = NodeCommand()
        cmd.execute_from_commandline()
