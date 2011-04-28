from restkit import ResourceNotFound, RequestError, RequestFailed

class NotConfigured(UserWarning):
    """Astral has not been configured, as no config module has been found."""
