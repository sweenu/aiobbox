"""Tests for BboxApi client."""

from asyncio import TimeoutError as asyncioTimeoutError
from typing import Any, Protocol
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from aiobbox import (
    BboxApi,
    BboxApiError,
    BboxInvalidCredentialsError,
    BboxRateLimitError,
    BboxSessionExpiredError,
    BboxTimeoutError,
    BboxUnauthenticatedError,
)


class MockResponseFactory(Protocol):
    """Protocol for mock response factory function."""

    def __call__(
        self,
        return_value: Any = None,
        status: int = 200,
        raise_for_status: bool = False,
    ) -> MagicMock: ...


@pytest.fixture
def api() -> BboxApi:
    """Fixture providing a BboxApi instance."""
    return BboxApi("test_password")


@pytest.fixture
async def authenticated_api(mock_session: AsyncMock) -> BboxApi:
    """Fixture providing an authenticated API client."""
    api = BboxApi("test_password")
    api._session = mock_session
    api._authenticated = True
    return api


class TestBboxApiInit:
    """Test suite for BboxApi initialization."""

    def test_init_default_values(self) -> None:
        """Test initialization with default values."""
        api = BboxApi("test_password")
        assert api.password == "test_password"
        assert api.base_url == "https://mabbox.bytel.fr/api/v1/"
        assert api.timeout == 10
        assert api._session is None
        assert api._authenticated is False

    def test_init_custom_values(self) -> None:
        """Test initialization with custom values."""
        api = BboxApi("custom_password", base_url="http://192.168.1.1/api/", timeout=30)
        assert api.password == "custom_password"
        assert api.base_url == "http://192.168.1.1/api/"
        assert api.timeout == 30

    def test_init_empty_password_raises_error(self) -> None:
        """Test that empty password raises ValueError."""
        with pytest.raises(ValueError, match="Password cannot be empty"):
            BboxApi("")


class TestBboxApiAuthentication:
    """Test suite for authentication functionality."""

    async def test_successful_authentication(
        self, api: BboxApi, mock_response_factory: MockResponseFactory
    ) -> None:
        """Test successful authentication flow."""
        mock_post_context = mock_response_factory(status=200)
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.post = MagicMock(return_value=mock_post_context)

        with patch("aiobbox.client.ClientSession", return_value=mock_session):
            await api.authenticate()
            assert api._authenticated is True
            assert api._session is not None
            mock_session.post.assert_called_once()

    @pytest.mark.parametrize(
        "status_code,error_class,error_substring",
        [
            (401, BboxInvalidCredentialsError, "Invalid password"),
            (429, BboxRateLimitError, "Rate limit exceeded"),
            (500, BboxApiError, "Authentication failed"),
        ],
    )
    async def test_authenticate_failure(
        self,
        api: BboxApi,
        status_code: int,
        error_class: type[BboxApiError],
        error_substring: str,
        mock_response_factory: MockResponseFactory,
    ) -> None:
        """Test authentication failures with various status codes."""
        mock_response_data = {"exception": {"errors": [{"reason": "test error"}]}}
        mock_post_context = mock_response_factory(
            return_value=mock_response_data, status=status_code
        )
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.post = MagicMock(return_value=mock_post_context)

        with (
            patch("aiobbox.client.ClientSession", return_value=mock_session),
            pytest.raises(error_class, match=error_substring),
        ):
            await api.authenticate()

    async def test_authenticate_timeout(self, api: BboxApi) -> None:
        """Test authentication timeout."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)

        with (
            patch("aiobbox.client.ClientSession", return_value=mock_session),
            patch("aiobbox.client.asyncio.timeout", side_effect=asyncioTimeoutError),
            pytest.raises(BboxTimeoutError, match="Authentication timeout"),
        ):
            await api.authenticate()

    async def test_authenticate_already_authenticated(
        self, authenticated_api: BboxApi
    ) -> None:
        """Test that re-authentication is skipped when already authenticated."""
        initial_session = authenticated_api._session
        await authenticated_api.authenticate()
        assert authenticated_api._session is initial_session


class TestBboxApiRequests:
    """Test suite for API request functionality."""

    async def test_request_unauthenticated_raises_error(self, api: BboxApi) -> None:
        """Test that requests fail when not authenticated."""
        with pytest.raises(
            BboxUnauthenticatedError, match="Not authenticated. Call authenticate"
        ):
            await api._request("GET", "device")

    async def test_request_success(
        self,
        authenticated_api: BboxApi,
        sample_device_data: dict[str, Any],
        mock_response_factory: MockResponseFactory,
    ) -> None:
        """Test successful API request."""
        mock_request_context = mock_response_factory(return_value=sample_device_data)
        assert authenticated_api._session is not None

        with patch.object(
            authenticated_api._session, "request", return_value=mock_request_context
        ):
            result = await authenticated_api._request("GET", "device")
            assert result == sample_device_data

    async def test_request_session_expired(self, authenticated_api: BboxApi) -> None:
        """Test handling of expired session."""
        error = aiohttp.ClientResponseError(
            request_info=MagicMock(), history=(), status=401
        )
        mock_request_context = MagicMock()
        mock_request_context.__aenter__ = AsyncMock(side_effect=error)
        mock_request_context.__aexit__ = AsyncMock(return_value=None)
        assert authenticated_api._session is not None

        with patch.object(
            authenticated_api._session, "request", return_value=mock_request_context
        ):
            with pytest.raises(BboxSessionExpiredError, match="Session expired"):
                await authenticated_api._request("GET", "device")
            assert authenticated_api._authenticated is False

    async def test_request_timeout(self, authenticated_api: BboxApi) -> None:
        """Test request timeout handling."""
        with (
            patch("aiobbox.client.asyncio.timeout", side_effect=TimeoutError),
            pytest.raises(BboxTimeoutError, match="Request timeout"),
        ):
            await authenticated_api._request("GET", "device")


class TestBboxApiMethods:
    """Test suite for API methods."""

    async def test_get_router_info(
        self,
        authenticated_api: BboxApi,
        sample_device_data: dict[str, Any],
        mock_response_factory: MockResponseFactory,
    ) -> None:
        """Test retrieving router information."""
        mock_request_context = mock_response_factory(return_value=sample_device_data)
        assert authenticated_api._session is not None

        with patch.object(
            authenticated_api._session, "request", return_value=mock_request_context
        ):
            router = await authenticated_api.get_router_info()
            assert router.modelname == "TestRouter3000"
            assert router.serialnumber == "123456789012345"

    async def test_get_hosts(
        self,
        authenticated_api: BboxApi,
        sample_hosts_list: dict[str, Any],
        mock_response_factory: MockResponseFactory,
    ) -> None:
        """Test retrieving hosts list."""
        mock_request_context = mock_response_factory(return_value=sample_hosts_list)
        assert authenticated_api._session is not None

        with patch.object(
            authenticated_api._session, "request", return_value=mock_request_context
        ):
            hosts = await authenticated_api.get_hosts()
            assert len(hosts) == 3
            assert hosts[0].hostname is None  # Empty string converted to None
            assert hosts[1].hostname == "office-printer"
            assert hosts[2].me is True

    async def test_get_wan_ip_stats(
        self,
        authenticated_api: BboxApi,
        sample_wan_stats_data: dict[str, Any],
        mock_response_factory: MockResponseFactory,
    ) -> None:
        """Test retrieving WAN IP statistics."""
        mock_request_context = mock_response_factory(return_value=sample_wan_stats_data)
        assert authenticated_api._session is not None

        with patch.object(
            authenticated_api._session, "request", return_value=mock_request_context
        ):
            stats = await authenticated_api.get_wan_ip_stats()
            assert stats.tx.bytes == 2400000
            assert stats.rx.bytes == 2500000


class TestBboxApiContextManager:
    """Test suite for async context manager functionality."""

    async def test_context_manager(
        self, mock_response_factory: MockResponseFactory
    ) -> None:
        """Test async context manager usage."""
        mock_post_context = mock_response_factory(status=200)
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.post = MagicMock(return_value=mock_post_context)
        mock_session.close = AsyncMock()

        with patch("aiobbox.client.ClientSession", return_value=mock_session):
            async with BboxApi("test_password") as api:
                assert api._authenticated is True
                assert api._session is not None
            mock_session.close.assert_called_once()

    async def test_close_method(self, api: BboxApi) -> None:
        """Test close method cleanup."""
        mock_session = AsyncMock(spec=aiohttp.ClientSession)
        mock_session.close = AsyncMock()
        api._session = mock_session
        api._owns_session = True
        api._authenticated = True

        await api.close()
        assert api._session is None
        assert api._authenticated is False
        mock_session.close.assert_called_once()
