from elixir import Field, Unicode, Entity, ManyToOne, Boolean, Text
from elixir.events import after_insert, before_insert
import json

from astral.models.base import BaseEntityMixin, slugify
from astral.models.event import Event


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48), primary_key=True)
    description = Field(Text)
    slug = Field(Unicode(48))
    streaming = Field(Boolean, default=False)
    source = ManyToOne('Node')

    def absolute_url(self):
        return '/stream/%s' % self.slug

    def tickets_url(self):
        return '%s/tickets' % self.absolute_url()

    def to_dict(self):
        return {'source': self.source.uuid, 'name': self.name,
                'slug': self.slug, 'description': self.description}

    @classmethod
    def from_dict(cls, data):
        stream = Stream.get_by(name=data['name'])
        if not stream:
            stream = cls(source=data['source'], name=data['name'],
                    description=data.get('description', ''))
        return stream

    @before_insert
    def set_slug(self):
        self.slug = self.slug or slugify(self.name)

    @after_insert
    def emit_new_stream_event(self):
        Event(message=json.dumps({'type': "stream", 'data': self.to_dict()}))

    def __repr__(self):
        return u'<Stream %s>' % self.slug
