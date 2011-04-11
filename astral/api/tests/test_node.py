from nose.tools import eq_
from tornado.httpclient import HTTPRequest

from astral.api.tests import BaseTest
from astral.models import Node
from astral.models.tests.factories import NodeFactory

class NodeHandlerTest(BaseTest):
    def test_delete_node(self):
        node = NodeFactory()
        self.http_client.fetch(HTTPRequest(
            self.get_url(node.absolute_url()), 'DELETE'), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Node.get_by(uuid=node.uuid), None)
