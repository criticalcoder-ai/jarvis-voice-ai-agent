class AccessControlError(Exception):
    """Base exception for access control errors."""
    def __init__(self, reason: str, action: str):
        super().__init__(reason)
        self.reason = reason
        self.action = action


class TierNotFoundError(AccessControlError):
    """Raised when a user's tier does not exist."""


class LimitExceededError(AccessControlError):
    """Raised when a usage or session limit is exceeded."""
