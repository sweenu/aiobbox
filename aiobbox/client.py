import asyncio
import logging
import types
from typing import Any
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponseError, ClientSession

from .models import Host, Router, WANIPStats

_LOGGER = logging.getLogger(__name__)


class BboxApiError(Exception):
    """Base exception for Bbox API errors."""


class BboxAuthError(BboxApiError):
    """Authentication error."""


class BboxApi:
    """Async Python API wrapper for Bbox routers."""

    def __init__(
        self,
        password: str,
        base_url: str = "https://mabbox.bytel.fr/api/v1/",
        timeout: int = 10,
        session: ClientSession | None = None,
    ) -> None:
        """Initialize the Bbox API client.

        Args:
            password: Router admin password
            base_url: Base URL (defaults to https://mabbox.bytel.fr/api/v1/)
            timeout: Request timeout in seconds
        """
        self.password = password
        self.base_url = base_url.rstrip("/") + "/"
        self.timeout = timeout

        self._session = session
        self._authenticated = False
        self._cookie_jar: aiohttp.CookieJar | None = None

    async def __aenter__(self) -> "BboxApi":
        await self.authenticate()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: types.TracebackType | None,
    ) -> None:
        await self.close()

    async def authenticate(self) -> None:
        """Authenticate to the Bbox API."""
        if self._authenticated and self._session:
            return

        try:
            if self._cookie_jar is None:
                self._cookie_jar = aiohttp.CookieJar()
            self._session = ClientSession(cookie_jar=self._cookie_jar)

            login_data = aiohttp.FormData()
            login_data.add_field("password", self.password)
            login_data.add_field("remember", "1")

            async with asyncio.timeout(self.timeout):
                url = urljoin(self.base_url, "login")
                response = await self._session.post(
                    url,
                    data=login_data,
                    headers={
                        "Referer": url,
                        "Origin": self.base_url.rstrip("/"),
                        "Content-Type": "application/x-www-form-urlencoded",
                    },
                )

                if response.status == 200:
                    self._authenticated = True
                    _LOGGER.debug("Successfully authenticated to Bbox")
                else:
                    await self._handle_auth_error(response)

        except ClientResponseError as err:
            if err.status == 401:
                raise BboxAuthError("Invalid credentials") from err
            _LOGGER.error("Authentication HTTP error: %s", err)
            raise BboxApiError(f"Authentication failed: {err}") from err
        except TimeoutError as err:
            _LOGGER.error("Authentication timeout")
            raise BboxApiError("Authentication timeout") from err
        except Exception as err:
            _LOGGER.error("Authentication error: %s", err)
            raise BboxApiError(f"Authentication failed: {err}") from err

    async def _handle_auth_error(self, response: aiohttp.ClientResponse) -> None:
        """Handle authentication errors."""
        status_code = response.status

        if status_code == 401:
            raise BboxAuthError("Invalid credentials")
        elif status_code == 429:
            # Extract rate limit details from response body
            try:
                error_data = await response.json()
                if (
                    isinstance(error_data, dict)
                    and "exception" in error_data
                    and "errors" in error_data["exception"]
                    and error_data["exception"]["errors"]
                ):
                    error_reason = error_data["exception"]["errors"][0].get(
                        "reason", ""
                    )
                    raise BboxApiError(f"Rate limit exceeded: {error_reason}")
            except Exception:
                # Fallback if parsing fails
                raise BboxApiError(
                    "Rate limit exceeded - too many login attempts"
                ) from None
        else:
            raise BboxApiError(f"Authentication failed with status {status_code}")

    async def _request(self, method: str, endpoint: str) -> Any:
        """Make an authenticated request to the Bbox API."""
        if not self._authenticated or not self._session:
            raise BboxApiError("Not authenticated")

        url = urljoin(self.base_url, endpoint)

        try:
            async with asyncio.timeout(self.timeout):
                response = await self._session.request(
                    method,
                    url,
                    headers={
                        "Referer": self.base_url,
                        "Origin": self.base_url.rstrip("/"),
                    },
                )

                if response.status == 401:
                    self._authenticated = False
                    raise BboxAuthError("Session expired, reauthentication required")

                response.raise_for_status()
                data = await response.json()

                # Bbox API returns arrays with single objects
                if isinstance(data, list) and len(data) == 1:
                    return data[0]
                return data

        except ClientResponseError as err:
            if err.status == 401:
                self._authenticated = False
                raise BboxAuthError("Session expired") from err
            _LOGGER.error("Request error for %s: %s", endpoint, err)
            raise BboxApiError(f"Request failed: {err}") from err
        except TimeoutError as err:
            _LOGGER.error("Request timeout for %s", endpoint)
            raise BboxApiError(f"Request timeout for {endpoint}") from err
        except Exception as err:
            _LOGGER.error("Unexpected error for %s: %s", endpoint, err)
            raise BboxApiError(f"Request failed: {err}") from err

    async def get_router_info(self) -> Router:
        """Get router information.

        Returns:
            Device: Router information
        """
        data = await self._request("GET", "device")
        return Router(**data["device"])

    async def get_hosts(self) -> list[Host]:
        """Get connected hosts information.

        Returns:
            list[Host]: List of connected hosts
        """
        data = await self._request("GET", "hosts")
        if isinstance(data, list):
            data = data[0]

        return [Host(**host_data) for host_data in data["hosts"]["list"]]

    async def get_wan_ip_stats(self) -> WANIPStats:
        """Get WAN IP statistics.

        Returns:
            WANIPStats: WAN statistics
        """
        data = await self._request("GET", "wan/ip/stats")
        return WANIPStats(**data["wan"]["ip"]["stats"])

    async def close(self) -> None:
        """Close the HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
            self._authenticated = False
