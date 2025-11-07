"""Bbox API exceptions with enhanced context."""

from typing import Any


class BboxApiError(Exception):
    """Base exception for Bbox API errors."""

    def __init__(
        self, message: str, *, status_code: int | None = None, **kwargs: Any
    ) -> None:
        """Initialize with optional context.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
            **kwargs: Additional context information
        """
        super().__init__(message)
        self.status_code = status_code
        self.context = kwargs


class BboxTimeoutError(BboxApiError):
    """Timeout error with duration context."""

    def __init__(self, message: str, *, timeout: float | None = None) -> None:
        """Initialize timeout error.

        Args:
            message: Error message
            timeout: Timeout duration in seconds
        """
        super().__init__(message, timeout=timeout)


class BboxUnauthenticatedError(BboxApiError):
    """Not authenticated error."""


class BboxRateLimitError(BboxApiError):
    """Rate limit error."""


class BboxAuthError(BboxApiError):
    """Authentication error."""


class BboxInvalidCredentialsError(BboxAuthError):
    """Invalid credentials error."""

    def __init__(self, message: str = "Invalid password") -> None:
        """Initialize invalid credentials error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=401)


class BboxSessionExpiredError(BboxAuthError):
    """Session expired error."""

    def __init__(self, message: str = "Session expired, re-authenticate") -> None:
        """Initialize session expired error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=401)
