from elixir import Field, Unicode, Integer, Entity

from astral.models.base import BaseEntityMixin


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48))

    API_FIELDS = ['id', 'name']

    def absolute_url(self):
        return '/stream/%s' % self.id
    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
