import Queue
from elixir import Field, Unicode, Entity

from astral.models.base import BaseEntityMixin

import logging
log = logging.getLogger(__name__)


EVENT_QUEUE = Queue.Queue()


class Event(BaseEntityMixin, Entity):
    message = Field(Unicode(96))

    def __init__(self, *args, **kwargs):
        kwargs['message'] = unicode(kwargs['message'])
        super(Event, self).__init__(*args, **kwargs)
        EVENT_QUEUE.put(self)

    def __repr__(self):
        return u'<Event %s>' % self.message
