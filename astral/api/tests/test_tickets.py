from nose.tools import eq_, ok_
from tornado.httpclient import HTTPRequest
import json
import mockito

from astral.api.tests import BaseTest
from astral.api.client import TicketsAPI, NodeAPI
from astral.models import Ticket, Node, session, Stream
from astral.models.tests.factories import (StreamFactory, NodeFactory,
        TicketFactory)

class TicketsHandlerTest(BaseTest):
    def setUp(self):
        super(TicketsHandlerTest, self).setUp()
        session.commit()
        mockito.when(NodeAPI).ping().thenReturn(42)
        mockito.when(TicketsAPI).confirm(mockito.any()).thenReturn(True)
        mockito.when(TicketsAPI).cancel(mockito.any()).thenReturn(True)

    def test_create(self):
        stream = StreamFactory(source=Node.me())
        node = NodeFactory()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST',
            body=json.dumps({'destination_uuid': node.uuid})), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('ticket' in result)
        eq_(result['ticket']['stream'], stream.slug)
        eq_(result['ticket']['source'], Node.me().uuid)
        ticket = Ticket.query.first()
        eq_(ticket.stream, stream)
        eq_(ticket.destination, node)

    def test_bad_destination(self):
        stream = StreamFactory()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST',
            body=json.dumps({'destination_uuid': 'foo'})), self.stop)
        response = self.wait()
        eq_(response.code, 404)

    def test_trigger_locally(self):
        stream = StreamFactory(source=Node.me())
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('ticket' in result)
        eq_(result['ticket']['stream'], stream.slug)
        eq_(result['ticket']['source'], Node.me().uuid)
        ticket = Ticket.query.first()
        eq_(ticket.stream, stream)
        eq_(ticket.destination, Node.me())

    def test_create_twice_locally(self):
        stream = StreamFactory(source=Node.me())
        TicketFactory(stream=stream, destination=Node.me())
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)

    def test_already_streaming(self):
        stream = StreamFactory(source=Node.me())
        TicketFactory(stream=stream, source=Node.me(), destination=Node.me())
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.query.count(), tickets_before)

    def test_already_seeding(self):
        stream = StreamFactory()
        TicketFactory(stream=stream, destination=Node.me())
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.query.count(), tickets_before)

    def test_other_known_tickets(self):
        stream = StreamFactory()
        existing_ticket = TicketFactory(stream=stream, source=stream.source,
                hops=1)
        mockito.when(TicketsAPI).create(mockito.any(),
                destination_uuid=mockito.any()).thenReturn(
                        {'source': existing_ticket.destination.uuid,
                            'source_port': 42,
                            'hops': 1})
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(
            self.get_url(stream.tickets_url()), 'POST', body=''),
            self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.query.count(), tickets_before + 1)
        ticket = Ticket.query.filter_by(destination=Node.me()).first()
        eq_(ticket.source, existing_ticket.destination)

    def test_remote_source(self):
        remote_node = NodeFactory()
        mockito.when(TicketsAPI).create(mockito.any(),
                destination_uuid=mockito.any()).thenReturn(
                        {'source': remote_node.uuid,
                            'source_port': 42,
                            'hops': 1})
        stream = StreamFactory()
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(self.get_url(stream.tickets_url()),
            'POST', body=''), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.query.count(), tickets_before + 1)

    def test_none_available(self):
        mockito.when(TicketsAPI).create(mockito.any(),
                destination_uuid=mockito.any()).thenReturn(None)
        stream = StreamFactory()
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(self.get_url(stream.tickets_url()),
            'POST', body=''), self.stop)
        response = self.wait()
        eq_(response.code, 412)
        eq_(Ticket.query.count(), tickets_before)

    def test_fallback_to_another_remote_node(self):
        # TODO node should be able to return a different source than itself
        remote_node = NodeFactory()
        mockito.when(TicketsAPI).create(mockito.any(),
                destination_uuid=mockito.any()).thenReturn(
                        {'source': remote_node.uuid,
                            'source_port': 42,
                            'hops': 1})
        stream = StreamFactory()
        tickets_before = Ticket.query.count()
        self.http_client.fetch(HTTPRequest(self.get_url(stream.tickets_url()),
            'POST', body=''), self.stop)
        response = self.wait()
        eq_(response.code, 200)
        eq_(Ticket.query.count(), tickets_before + 1)

class TicketsListHandlerTest(BaseTest):
    def setUp(self):
        super(TicketsListHandlerTest, self).setUp()
        Node.me()
        [TicketFactory() for _ in range(3)]

    def test_get_tickets(self):
        response = self.fetch('/tickets')
        eq_(response.code, 200)
        result = json.loads(response.body)
        ok_('tickets' in result)
        eq_(len(result['tickets']), 3)
        for ticket in result['tickets']:
            source = Node.get_by(uuid=ticket['source'])
            destination = Node.get_by(uuid=ticket['destination'])
            ok_(Ticket.get_by(stream=Stream.get_by(slug=ticket['stream']),
                source=source, destination=destination))
