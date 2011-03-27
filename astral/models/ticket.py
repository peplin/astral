from elixir import ManyToOne, Entity

from astral.models.base import BaseEntityMixin


class Ticket(BaseEntityMixin, Entity):
    node = ManyToOne('Node')
    stream = ManyToOne('Stream')

    def __repr__(self):
        return u'<Ticket %s: %s to %s>' % (self.id, self.stream, self.node)