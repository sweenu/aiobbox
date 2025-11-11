"""Async Python API wrapper for Bouygues Telecom routers."""

__version__ = "0.3.1"

from .client import BboxApi
from .exceptions import (
    BboxApiError,
    BboxAuthError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxSessionExpiredError,
    BboxTimeoutError,
    BboxUnauthenticatedError,
)
from .models import (
    Host,
    Router,
    WANIPStats,
    WANStats,
)

__all__ = [
    "BboxApi",
    "BboxApiError",
    "BboxAuthError",
    "BboxInvalidCredentialsError",
    "BboxRateLimitError",
    "BboxSessionExpiredError",
    "BboxTimeoutError",
    "BboxUnauthenticatedError",
    "Router",
    "Host",
    "Hosts",
    "WANIPStats",
    "WANStats",
]
