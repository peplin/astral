from nose.tools import eq_, ok_
import json

from astral.api.tests import BaseTest
from astral.models.node import Node
from astral.models.tests.factories import NodeFactory

class NodesHandlerTest(BaseTest):
    def test_get_nodes(self):
        nodes = [NodeFactory() for _ in range(3)]
        response = self.fetch('/nodes')
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('nodes' in result)
        for node in result['nodes']:
            ok_(Node.get_by(uuid=node['uuid']))
