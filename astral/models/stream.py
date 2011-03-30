from elixir import Field, Unicode, Entity, ManyToOne
from elixir.events import after_insert
import json

from astral.models.base import BaseEntityMixin
from astral.models.event import Event


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48))
    source = ManyToOne('Node')

    API_FIELDS = ['id', 'name', 'source']

    def absolute_url(self):
        return '/stream/%s' % self.id

    def tickets_url(self):
        return '%s/tickets' % self.absolute_url()

    @after_insert
    def emit_new_node_event(self):
        Event(message=json.dumps({'type': "stream", 'data': self.to_dict()}))

    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
