import re


class BaseEntityMixin(object):
    def to_dict(self):
        return dict(((field, getattr(self, field))
                for field in self.API_FIELDS))


def slugify(value):
    """
    Normalizes string, converts to lowercase, removes non-alpha characters,
    and converts spaces to hyphens.

    Borrow from Django.
    """
    value = unicode(re.sub('[^\w\s-]', '', value).strip().lower())
    return re.sub('[-\s]+', '-', value)
