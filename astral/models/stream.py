from elixir import Entity, Field, Unicode, Integer


class Stream(Entity):
    name = Field(Unicode(48))

    def absolute_url(self):
        return '/stream/%s' % self.id

    def to_dict(self):
        return {'name': self.name}

    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
