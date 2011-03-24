"""Borrowed from Django."""

from threading import Lock

class LazyObject(object):
    """
    A wrapper for another class that can be used to delay instantiation of the
    wrapped class.

    By subclassing, you have the opportunity to intercept and alter the
    instantiation. If you don't need to do that, use SimpleLazyObject.
    """
    def __init__(self):
        self._wrapped = None
        self._lock = Lock()

    def __getattr__(self, name):
        self._lock.acquire()
        if self._wrapped is None:
            self._setup()
        self._lock.release()
        return getattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name in ["_wrapped", "_lock"]:
            # Assign to __dict__ to avoid infinite __setattr__ loops.
            self.__dict__[name] = value
        else:
            if self._wrapped is None:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if self._wrapped is None:
            self._setup()
        delattr(self._wrapped, name)

    def _setup(self):
        """
        Must be implemented by subclasses to initialise the wrapped object.
        """
        raise NotImplementedError

    # introspection support:
    __members__ = property(lambda self: self.__dir__())

    def __dir__(self):
        if self._wrapped is None:
            self._setup()
        return  dir(self._wrapped)
