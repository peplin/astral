from elixir import Field, Unicode, Entity, ManyToOne

from astral.models.base import BaseEntityMixin


class Stream(BaseEntityMixin, Entity):
    name = Field(Unicode(48))
    source = ManyToOne('Node')

    API_FIELDS = ['id', 'name', 'source']

    def absolute_url(self):
        return '/stream/%s' % self.id

    def __repr__(self):
        return u'<Stream %s: %s>' % (self.id, self.name)
