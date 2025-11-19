"""Custom exception classes for Metering Service."""


class MeteringException(Exception):
    """Base exception for metering service."""
    pass


class ValidationError(MeteringException):
    """Raised when validation fails."""
    pass


class QuotaExceededError(MeteringException):
    """Raised when quota is exceeded."""
    pass


class DatabaseError(MeteringException):
    """Raised when database operation fails."""
    pass


class CacheError(MeteringException):
    """Raised when cache operation fails."""
    pass


class AuthenticationError(MeteringException):
    """Raised when authentication fails."""
    pass

