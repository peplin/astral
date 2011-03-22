from elixir import Entity, ManyToOne


class Ticket(Entity):
    node = ManyToOne('Node')
    stream = ManyToOne('Stream')

    def __repr__(self):
        return u'<Ticket %s: %s to %s>' % (self.id, self.stream, self.node)
