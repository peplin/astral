import unittest2 
from nose.tools import raises

from astral.bin.astralnode import NodeCommand

class NodeCommandTest(unittest2.TestCase):
    @raises(SystemExit)
    def test_basic_run(self):
        cmd = NodeCommand()
        cmd.execute_from_commandline(argv=["astralnode", "-h"])
