class AccessControlError(Exception):
    """Base exception for access control errors."""


class TierNotFoundError(AccessControlError):
    """Raised when a user's tier does not exist."""


class LimitExceededError(AccessControlError):
    """Raised when a usage or session limit is exceeded."""
