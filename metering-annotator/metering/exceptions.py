"""Custom exceptions for Metering Annotator."""


class MeteringError(Exception):
    """Base exception for metering annotator."""
    pass


class MeteringAPIError(MeteringError):
    """Raised when API call fails."""
    pass


class MeteringConfigError(MeteringError):
    """Raised when configuration is invalid."""
    pass

