"""
astral.datastructures
=====================

Custom data structures, borrowed from the Celery project.

:copyright: (c) 2009 - 2011 by Ask Solem.
:license: BSD, see LICENSE for more details.

"""
from itertools import chain

class AttributeDictMixin(object):
    """Adds attribute access to mappings.

    `d.key -> d[key]`

    """

    def __getattr__(self, key):
        """`d.key -> d[key]`"""
        try:
            return self[key]
        except KeyError:
            raise AttributeError("'%s' object has no attribute '%s'" % (
                    self.__class__.__name__, key))

    def __setattr__(self, key, value):
        """`d[key] = value -> d.key = value`"""
        self[key] = value


class AttributeDict(dict, AttributeDictMixin):
    """Dict subclass with attribute access."""
    pass


class ConfigurationView(AttributeDictMixin):
    changes = None
    defaults = None

    def __init__(self, changes, defaults):
        self.__dict__["changes"] = changes
        self.__dict__["defaults"] = defaults
        self.__dict__["_order"] = [changes] + defaults

    def __getitem__(self, key):
        for d in self.__dict__["_order"]:
            try:
                return d[key]
            except KeyError:
                pass
        raise KeyError(key)

    def __setitem__(self, key, value):
        self.__dict__["changes"][key] = value

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def setdefault(self, key, default):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def update(self, *args, **kwargs):
        return self.__dict__["changes"].update(*args, **kwargs)

    def __contains__(self, key):
        for d in self.__dict__["_order"]:
            if key in d:
                return True
        return False

    def __repr__(self):
        return repr(dict(iter(self)))

    def __iter__(self):
        # defaults must be first in the stream, so values in
        # in changes takes precedence.
        return chain(*[d.iteritems()
                        for d in reversed(self.__dict__["_order"])])

    def iteritems(self):
        return iter(self)

    def items(self):
        return tuple(self.iteritems())
