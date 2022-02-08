class DoesNotExist(Exception):
    """Raised when entity was not found in database."""


class AlreadyExists(Exception):
    """Raised when entity already exists with matching unique data."""
