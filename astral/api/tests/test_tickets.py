from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest
import json

from astral.api.tests import BaseTest
from astral.models import Ticket, Node
from astral.models.tests.factories import (StreamFactory, NodeFactory,
        ThisNodeFactory)

class TicketsHandlerTest(BaseTest):
    def setUp(self):
        super(TicketsHandlerTest, self).setUp()
        ThisNodeFactory()

    def test_create(self):
        stream = StreamFactory()
        node = NodeFactory()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST',
            body=json.dumps({'destination_uuid': node.uuid})), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('stream' in result)
        eq_(result['stream']['id'], stream.id)
        eq_(result['stream']['name'], stream.name)
        ticket = Ticket.query.first()
        eq_(ticket.stream, stream)
        eq_(ticket.destination, node)

    def test_trigger_locally(self):
        stream = StreamFactory()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('stream' in result)
        eq_(result['stream']['id'], stream.id)
        eq_(result['stream']['name'], stream.name)
        ticket = Ticket.query.first()
        eq_(ticket.stream, stream)
        eq_(ticket.destination, Node.me())
