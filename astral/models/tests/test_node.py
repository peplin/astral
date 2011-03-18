import unittest2 
from nose.tools import ok_, eq_, assert_not_equal
import mockito
import restkit

from astral.models.node import Node
from astral.api.client import NodeAPI


class NodeTest(unittest2.TestCase):
    def setUp(self):
        super(NodeTest, self).setUp()
        self.node = Node(ip_address='localhost', port='8000')

    def test_update_rtt_error(self):
        mockito.when(NodeAPI).ping().thenRaise(restkit.RequestError())

    def test_update_rtt(self):
        mockito.when(NodeAPI).ping().thenReturn(None)
        eq_(self.node.rtt, None)
        rtt = self.node.update_rtt()
        eq_(self.node.rtt, rtt)
        assert_not_equal(rtt, None)

    def test_weighted_rtt(self):
        mockito.when(NodeAPI).ping().thenReturn(None)
        self.node.rtt = 100
        rtt = self.node.update_rtt()
        ok_(rtt < 100)
        ok_(rtt > 10)
