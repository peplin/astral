from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest
import json

from astral.api.tests import BaseTest
from astral.models import Ticket, Stream, Node
from astral.models.tests.factories import TicketFactory

class TicketHandlerTest(BaseTest):
    def test_delete(self):
        node = Node.me()
        ticket = TicketFactory(destination=node)
        self.http_client.fetch(HTTPRequest(
            self.get_url(ticket.absolute_url()), 'DELETE'), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.get_by(id=ticket.id), None)
        ok_(Stream.get_by(slug=ticket.stream.slug))

    def test_get(self):
        node = Node.me()
        ticket = TicketFactory(destination=node)
        response = self.fetch(ticket.absolute_url())
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('ticket' in result)
        eq_(result['ticket']['stream'], ticket.stream.slug)

    def test_confirm(self):
        node = Node.me()
        ticket = TicketFactory(destination=node, confirmed=False)
        data = {'confirmed': True}
        eq_(ticket.confirmed, False)
        self.http_client.fetch(HTTPRequest(
            self.get_url(ticket.absolute_url()), 'PUT', body=json.dumps(data)),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(ticket.confirmed, True)
