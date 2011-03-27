class NotConfigured(UserWarning):
    """Astral has not been configured, as no config module has been found."""

class NetworkError(Exception):
    """Can't contact the origin webserver."""
