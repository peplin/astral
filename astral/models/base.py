class BaseEntityMixin(object):
    def to_dict(self):
        return dict(((field, getattr(self, field))
                for field in self.API_FIELDS))

