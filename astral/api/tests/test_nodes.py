from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest
import json

from astral.api.tests import BaseTest
from astral.models.node import Node
from astral.models.tests.factories import NodeFactory

class NodesHandlerTest(BaseTest):
    def test_get_nodes(self):
        [NodeFactory() for _ in range(3)]
        response = self.fetch('/nodes')
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('nodes' in result)
        for node in result['nodes']:
            ok_(Node.get_by(uuid=node['uuid']))

    def test_register_node(self):
        data = {'uuid': "a-unique-id", 'port': 8001}
        eq_(Node.get_by(uuid=data['uuid']), None)
        self.http_client.fetch(HTTPRequest(
            self.get_url('/nodes'), 'POST', body=json.dumps(data)), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        ok_(Node.get_by(uuid=data['uuid']))
