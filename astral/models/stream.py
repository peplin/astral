from elixir import Entity, Field, Unicode


class Stream(Entity):
    name = Field(Unicode(48))

    def to_dict(self):
        return {'name': self.name}

    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
