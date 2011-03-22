from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest

from astral.api.tests import BaseTest
from astral.models import Ticket, Node, Stream
from astral.models.tests.factories import TicketFactory

class StreamHandlerTest(BaseTest):
    def test_delete_stream_ticket(self):
        node = Node(ip_address='127.0.0.1')
        ticket = TicketFactory(node=node)
        self.http_client.fetch(HTTPRequest(
            self.get_url(ticket.stream.absolute_url()), 'DELETE'), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.get_by(id=ticket.id), None)
        ok_(Stream.get_by(id=ticket.stream.id))
