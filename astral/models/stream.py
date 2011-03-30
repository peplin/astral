from elixir import Field, Unicode, Entity, ManyToOne
from elixir.events import after_insert
import json

from astral.models.base import BaseEntityMixin
from astral.models.event import Event


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48))
    source = ManyToOne('Node')

    def absolute_url(self):
        return '/stream/%s' % self.id

    def tickets_url(self):
        return '%s/tickets' % self.absolute_url()

    def to_dict(self):
        return {'source': self.source.uuid, 'name': self.name, 'id': self.id}

    @after_insert
    def emit_new_stream_event(self):
        Event(message=json.dumps({'type': "stream", 'data': self.to_dict()}))

    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
