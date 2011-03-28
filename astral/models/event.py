import Queue
from elixir import Field, Unicode, Entity

from astral.models.base import BaseEntityMixin

import logging
log = logging.getLogger(__name__)


EVENT_QUEUE = Queue.Queue()


class Event(BaseEntityMixin, Entity):
    message = Field(Unicode(96))

    def save(self, *args, **kwargs):
        super(Event, self).save(*args, **kwargs)
        EVENT_QUEUE.put(self)

    def __repr__(self):
        return u'<Event %s>' % self.message
