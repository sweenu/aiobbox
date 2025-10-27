"""Async Python API wrapper for Bouygues Telecom routers."""

__version__ = "0.1.0"

from .client import BboxApi, BboxApiError, BboxAuthError
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
    "Router",
    "Host",
    "Hosts",
    "WANIPStats",
    "WANStats",
]
