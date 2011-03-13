class NotConfigured(UserWarning):
    """Astral has not been configured, as no config module has been found."""

class OriginWebserverError(Exception):
    """Can't contact the origin webserver."""
