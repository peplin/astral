from elixir import ManyToOne, Entity, Boolean, Field, DateTime, Integer
from elixir.events import after_insert, before_insert, after_update
import json
import datetime
import Queue

from astral.conf import settings
from astral.models.base import BaseEntityMixin
from astral.models.event import Event
from astral.models.node import Node

TUNNEL_QUEUE = Queue.Queue()

class Ticket(Entity, BaseEntityMixin):
    source = ManyToOne('Node')
    source_port = Field(Integer)
    destination = ManyToOne('Node')
    destination_port = Field(Integer)
    stream = ManyToOne('Stream')
    confirmed = Field(Boolean, default=False)
    created = Field(DateTime)

    def __init__(self, source=None, source_port=None, destination=None,
            destination_port=None, *args, **kwargs):
        source = source or Node.me()
        source_port = source_port or settings.RTMP_PORT
        destination = destination or Node.me()
        destination_port = destination_port or settings.RTMP_TUNNEL_PORT
        super(Ticket, self).__init__(source=source, source_port=source_port,
                destination=destination, destination_port=destination_port,
                *args, **kwargs)

    def absolute_url(self):
        return '/stream/%s/ticket/%s' % (self.stream.slug,
                self.destination.uuid)

    def to_dict(self):
        return {'source': self.source.uuid,
                'source_port': self.source_port,
                'destination': self.destination.uuid,
                'destination_port': self.destination_port,
                'stream': self.stream.slug}

    @classmethod
    def unconfirmed(cls, query=None):
        query = query or cls.query
        return query.filter_by(confirmed=False)

    @classmethod
    def old(cls, query=None):
        query = query or cls.query
        now = datetime.datetime.now()
        one_day_ago = now - datetime.timedelta(
                days=settings.UNCONFIRMED_TICKET_EXPIRATION)
        return query.filter(Ticket.created < one_day_ago)

    @after_insert
    def emit_new_ticket_event(self):
        Event(message=json.dumps({'type': "ticket", 'data': self.to_dict()}))

    @after_insert
    @after_update
    def queue_tunnel_creation(self):
        """Since Astral is a "pull" system, the person receiving a forwarded
        stream from us based on this ticket (the destination) is in charge of
        connecting to us - we don't explicitly send anything to them.

        This will queue the node up to create a tunnel from the source's RTMP
        server to a port on the local node. If we created this ticket for
        ourselves, we will just connect to it from the browser. If it was
        created in response to a request from another node (i.e. the destination
        is not us), we don't create any extra tunnels. A tunnel will already
        exist in that case to bring the stream from somewhere else to here.
        """
        if self.confirmed and self.destination == Node.me():
            TUNNEL_QUEUE.put(self.id)

    @before_insert
    def set_created_time(self):
        if not self.created:
            self.created = datetime.datetime.now()

    def __repr__(self):
        return u'<Ticket %s: %s from %s to %s>' % (
                self.id, self.stream, self.source, self.destination)
