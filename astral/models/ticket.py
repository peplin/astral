from elixir import ManyToOne, Entity

from astral.models.base import BaseEntityMixin


class Ticket(BaseEntityMixin, Entity):
    source = ManyToOne('Node')
    destination = ManyToOne('Node')
    stream = ManyToOne('Stream')

    def absolute_url(self):
        return '/stream/%s/ticket/%s' % (self.stream.id,
                self.destination.uuid)

    def __repr__(self):
        return u'<Ticket %s: %s from %s to %s>' % (
                self.id, self.stream, self.source, self.destination)
