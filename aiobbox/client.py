"""Async Python API wrapper for Bbox routers."""

import asyncio
import logging
from http import HTTPStatus
from typing import Any, ClassVar, Self
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponseError, ClientSession

from .exceptions import (
    BboxApiError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxSessionExpiredError,
    BboxTimeoutError,
    BboxUnauthenticatedError,
)
from .models import Host, Router, WANIPStats

_LOGGER = logging.getLogger(__name__)


class BboxApi:
    """Async Python API wrapper for Bbox routers."""

    DEFAULT_BASE_URL: ClassVar[str] = "https://mabbox.bytel.fr/api/v1/"
    DEFAULT_TIMEOUT: ClassVar[int] = 10

    def __init__(
        self,
        password: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize the Bbox API client.

        Args:
            password: Router admin password
            base_url: Base URL for API requests
            timeout: Request timeout in seconds
            session: Optional existing aiohttp session

        Raises:
            ValueError: If password is empty
        """
        if not password:
            raise ValueError("Password cannot be empty")

        self.password = password
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout
        self._session = session
        self._authenticated = False
        self._cookie_jar: aiohttp.CookieJar | None = None
        self._owns_session = False  # Track if we created the session

        _LOGGER.debug("Initialized BboxApi client with base_url=%s", self.base_url)

    async def __aenter__(self) -> Self:
        """Async context manager entry.

        Returns:
            Self: The authenticated API client

        Raises:
            BboxTimeoutError: If authentication times out
            BboxInvalidCredentialsError: If credentials are invalid
            BboxRateLimitError: If rate limit is exceeded
            BboxApiError: For other API errors
        """
        await self.authenticate()
        return self

    async def __aexit__(self, *_: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def authenticate(self) -> None:
        """Authenticate to the Bbox API.

        Raises:
            BboxTimeoutError: If authentication times out
            BboxInvalidCredentialsError: If credentials are invalid
            BboxRateLimitError: If rate limit is exceeded
            BboxApiError: For other API errors
        """
        if self._authenticated and self._session:
            _LOGGER.debug("Already authenticated, skipping")
            return

        if self._session is None:
            self._cookie_jar = aiohttp.CookieJar()
            self._session = ClientSession(cookie_jar=self._cookie_jar)
            self._owns_session = True
            _LOGGER.debug("Created new aiohttp session")

        login_data = aiohttp.FormData()
        login_data.add_field("password", self.password)
        login_data.add_field("remember", "1")

        url = urljoin(self.base_url, "login")

        try:
            async with asyncio.timeout(self.timeout):
                async with self._session.post(
                    url,
                    data=login_data,
                    headers={
                        "Referer": url,
                        "Origin": self.base_url.rstrip("/"),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                ) as response:
                    if response.status == HTTPStatus.OK:
                        self._authenticated = True
                        _LOGGER.info("Successfully authenticated to Bbox")
                    else:
                        await self._handle_auth_error(response)
        except TimeoutError as err:
            _LOGGER.error("Authentication timeout after %ds", self.timeout)
            raise BboxTimeoutError(
                "Authentication timeout", timeout=float(self.timeout)
            ) from err

    async def _handle_auth_error(self, response: aiohttp.ClientResponse) -> None:
        """Handle authentication errors with structured error handling.

        Args:
            response: The aiohttp response object

        Raises:
            BboxInvalidCredentialsError: If credentials are invalid (401)
            BboxRateLimitError: If rate limit is exceeded (429)
            BboxApiError: For other authentication failures
        """
        status_code = response.status

        try:
            error_data = await response.json()
        except aiohttp.ClientError:
            reason = None
        else:
            reason = (
                error_data.get("exception", {}).get("errors", [{}])[0].get("reason")
            )

        match status_code:
            case 401:
                _LOGGER.error("Invalid credentials")
                raise BboxInvalidCredentialsError("Invalid password")
            case 429:
                error_msg = (
                    f"Rate limit exceeded: {reason or 'too many login attempts'}"
                )
                _LOGGER.error(error_msg)
                raise BboxRateLimitError(error_msg)
            case _:
                error_msg = f"Authentication failed with status {status_code}"
                if reason:
                    error_msg += f": {reason}"
                _LOGGER.error(error_msg)
                raise BboxApiError(error_msg, status_code=status_code)

    async def close(self) -> None:
        """Close the HTTP session if we own it."""
        if self._session and self._owns_session:
            await self._session.close()
            _LOGGER.debug("Closed aiohttp session")

        self._session = None
        self._authenticated = False
        self._cookie_jar = None

    async def _request(self, method: str, endpoint: str) -> Any:
        """Make an authenticated request to the Bbox API.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path

        Returns:
            Parsed JSON response

        Raises:
            BboxUnauthenticatedError: If not authenticated
            BboxSessionExpiredError: If session has expired
            BboxTimeoutError: If request times out
            BboxApiError: For other API errors
        """
        if not self._authenticated or not self._session:
            raise BboxUnauthenticatedError(
                "Not authenticated. Call authenticate() first."
            )

        url = urljoin(self.base_url, endpoint)

        try:
            async with asyncio.timeout(self.timeout):
                async with self._session.request(
                    method,
                    url,
                    headers={
                        "Referer": self.base_url,
                        "Origin": self.base_url.rstrip("/"),
                    },
                    allow_redirects=True,
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

        except TimeoutError as err:
            _LOGGER.error("Request timeout for %s after %ds", endpoint, self.timeout)
            raise BboxTimeoutError(
                f"Request timeout for {endpoint}", timeout=float(self.timeout)
            ) from err

        except ClientResponseError as err:
            if err.status == 401:
                self._authenticated = False
                _LOGGER.warning("Session expired for %s", endpoint)
                raise BboxSessionExpiredError(
                    "Session expired, re-authenticate"
                ) from err

            _LOGGER.error("HTTP %d error for %s: %s", err.status, endpoint, err)
            raise BboxApiError(
                f"Request failed with HTTP {err.status}: {err}", status_code=err.status
            ) from err

        except aiohttp.ClientError as err:
            _LOGGER.error("Client error for %s: %s", endpoint, err)
            raise BboxApiError(f"Request failed: {err}") from err

        # Bbox API returns arrays with single objects
        if isinstance(data, list) and len(data) == 1:
            return data[0]

        return data

    async def get_router_info(self) -> Router:
        """Get router device information.

        Returns:
            Router information

        Raises:
            BboxUnauthenticatedError: If not authenticated
            BboxSessionExpiredError: If session has expired
            BboxTimeoutError: If request times out
            BboxApiError: For other API errors
        """
        _LOGGER.debug("Fetching router info")
        data = await self._request("GET", "device")
        return Router(**data["device"])

    async def get_hosts(self) -> list[Host]:
        """Get list of connected hosts/devices.

        Returns:
            List of connected hosts

        Raises:
            BboxUnauthenticatedError: If not authenticated
            BboxSessionExpiredError: If session has expired
            BboxTimeoutError: If request times out
            BboxApiError: For other API errors
        """
        _LOGGER.debug("Fetching hosts list")
        data = await self._request("GET", "hosts")
        if isinstance(data, list):
            data = data[0]
        return [Host(**host_data) for host_data in data["hosts"]["list"]]

    async def get_wan_ip_stats(self) -> WANIPStats:
        """Get WAN IP statistics.

        Returns:
            WAN IP statistics

        Raises:
            BboxUnauthenticatedError: If not authenticated
            BboxSessionExpiredError: If session has expired
            BboxTimeoutError: If request times out
            BboxApiError: For other API errors
        """
        _LOGGER.debug("Fetching WAN IP stats")
        data = await self._request("GET", "wan/ip/stats")
        return WANIPStats(**data["wan"]["ip"]["stats"])
