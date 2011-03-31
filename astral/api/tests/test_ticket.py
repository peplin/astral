from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest

from astral.api.tests import BaseTest
from astral.models import Ticket, Stream, Node
from astral.models.tests.factories import TicketFactory, ThisNodeFactory

class TicketHandlerTest(BaseTest):
    def test_delete(self):
        ThisNodeFactory()
        ticket = TicketFactory(destination=Node.me())
        self.http_client.fetch(HTTPRequest(
            self.get_url(ticket.absolute_url()), 'DELETE'), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.get_by(id=ticket.id), None)
        ok_(Stream.get_by(id=ticket.stream.id))
