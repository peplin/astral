from elixir import ManyToOne, Entity, Boolean, Field, DateTime
from elixir.events import after_insert, before_insert
import json
import datetime

from astral.conf import settings
from astral.models.base import BaseEntityMixin
from astral.models.event import Event
from astral.models.node import Node


class Ticket(Entity, BaseEntityMixin):
    source = ManyToOne('Node')
    destination = ManyToOne('Node')
    stream = ManyToOne('Stream')
    confirmed = Field(Boolean, default=False)
    created = Field(DateTime)

    def __init__(self, source=None, destination=None, *args, **kwargs):
        source = source or Node.me()
        destination = destination or Node.me()
        super(Ticket, self).__init__(source=source,
                destination=destination, *args, **kwargs)

    def absolute_url(self):
        return '/stream/%s/ticket/%s' % (self.stream.slug,
                self.destination.uuid)

    def to_dict(self):
        return {'source': self.source.uuid,
                'destination': self.destination.uuid,
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

    @before_insert
    def set_created_time(self):
        if not self.created:
            self.created = datetime.datetime.now()

    def __repr__(self):
        return u'<Ticket %s: %s from %s to %s>' % (
                self.id, self.stream, self.source, self.destination)
