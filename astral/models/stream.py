from elixir import Field, Unicode, Entity, ManyToOne, Boolean, Text, Integer
from elixir.events import after_insert, before_insert, after_update
import json

from astral.models import session, Node
from astral.models.ticket import TUNNEL_QUEUE
from astral.models.base import BaseEntityMixin, slugify
from astral.models.event import Event

import logging
log = logging.getLogger(__name__)


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48), primary_key=True)
    description = Field(Text)
    slug = Field(Unicode(48))
    streaming = Field(Boolean, default=False)
    source = ManyToOne('Node')
    # the local tunnel, this value is only set on the source
    source_port = Field(Integer)

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
            source = Node.get_by(uuid=data.get('source') or
                    data.get('source_uuid'))
            if not source:
                log.debug("%s had a source not in our database -- not creating " 
                        "Stream", data)
                return
            else:
                stream = cls(source=source, name=data['name'],
                        description=data.get('description', ''))
                session.commit()
        return stream

    @before_insert
    def set_slug(self):
        self.slug = self.slug or slugify(self.name)

    @after_insert
    def emit_new_stream_event(self):
        Event(message=json.dumps({'type': "stream", 'data': self.to_dict()}))

    @after_insert
    @after_update
    def queue_tunnel_status_flip(self):
        """If the stream went from disable to enable or vice versa, need to flip
        the status of the tunnel. Also, every local stream needs a local tunnel
        so we have something to control.
        """
        if self.source == Node.me():
            TUNNEL_QUEUE.put(self)

    def __repr__(self):
        return u'<Stream %s, from %s>' % (self.slug, self.source)
