from unittest.mock import AsyncMock, Mock, patch

import pytest

from aiobbox import BboxApi, BboxApiError


class TestBboxApi:
    @pytest.fixture
    def api(self) -> BboxApi:
        api = BboxApi("test_password")
        # Don't create cookie jar during test setup
        api._cookie_jar = None
        return api

    @pytest.fixture
    def sample_device_data(self) -> dict:
        """Fixture providing sample device data."""
        return {
            "now": "2025-10-27T21:14:33+0100",
            "status": 1,
            "numberofboots": 10,
            "modelname": "F@st5696b",
            "modelclass": "F5696b",
            "optimisation": 1,
            "user_configured": 1,
            "serialnumber": "123456789012345",
            "display": {
                "luminosity": 2,
                "luminosity_extender": 100,
                "state": ".",
            },
            "main": {"version": "25.5.28", "date": "2025-09-25T14:38:50Z"},
            "reco": {"version": "25.5.28", "date": "2025-09-25T14:29:16Z"},
            "running": {
                "version": "25.5.28",
                "date": "2025-09-25T14:38:16+0000",
            },
            "spl": {"version": ""},
            "tpl": {"version": ""},
            "ldr1": {"version": "4.4.20"},
            "ldr2": {"version": "4.4.20"},
            "firstusedate": "2025-07-23T06:30:42Z",
            "uptime": 404347,
            "lastFactoryReset": 0,
            "using": {"ipv4": 1, "ipv6": 1, "ftth": 1, "adsl": 0, "vdsl": 0},
            "isCellularEnable": 1,
            "newihm": 1,
            "newihmCdc": 1,
        }

    @pytest.fixture
    def sample_host_data(self) -> dict:
        """Fixture providing sample host data."""
        return {
            "id": 1,
            "active": 1,
            "devicetype": "wifi",
            "duid": "test-duid",
            "guest": 0,
            "hostname": "test-device",
            "ipaddress": "192.168.1.100",
            "lease": 0,
            "link": "wireless",
            "macaddress": "aa:bb:cc:dd:ee:ff",
            "type": "wireless",
            "firstseen": "2025-10-27T21:14:33+0100",
            "lastseen": 1730052873,
            "serialNumber": "",
            "ip6address": [],
            "ethernet": {
                "physicalport": 0,
                "logicalport": 0,
                "speed": 0,
                "mode": "auto",
            },
            "wireless": {
                "wexindex": 0,
                "static": 0,
                "band": "2.4GHz",
                "txUsage": 0,
                "rxUsage": 0,
                "estimatedRate": 0,
                "rssi0": 0,
                "mcs": 0,
                "rate": 0,
            },
            "wirelessByBand": [],
            "plc": {
                "rxphyrate": "100Mbps",
                "txphyrate": "100Mbps",
                "associateddevice": 0,
                "interface": 0,
                "ethernetspeed": 0,
            },
            "informations": {
                "type": "TÃ©lÃ©phone",
                "manufacturer": "Test Manufacturer",
                "model": "Test Model",
                "icon": "telephone",
                "operatingSystem": "Test OS",
                "version": "1.0",
            },
            "parentalcontrol": {
                "enable": 0,
                "status": "enabled",
                "statusRemaining": 0,
                "statusUntil": 0,
            },
            "ping": {
                "average": 0,
            },
            "scan": {
                "services": [],
            },
        }

    @pytest.fixture
    def sample_wan_stats_data(self) -> dict:
        """Fixture providing sample WAN stats data."""
        return {
            "rx": {
                "packets": 104522008,
                "bytes": 130580798930,
                "packetserrors": 0,
                "packetsdiscards": 0,
                "occupation": 0,
                "bandwidth": 29,
                "maxBandwidth": 1000000,
                "contractualBandwidth": 8000000,
            },
            "tx": {
                "packets": 11135558,
                "bytes": 5471690248,
                "packetserrors": 0,
                "packetsdiscards": 0,
                "occupation": 0,
                "bandwidth": 10,
                "maxBandwidth": 1000000,
                "contractualBandwidth": 1000000,
            },
        }

    @pytest.mark.asyncio
    async def test_authenticate_success(self, api: BboxApi) -> None:
        """Test successful authentication."""
        with patch("aiobbox.client.ClientSession") as MockSession:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            # Mock the post method to return our async context manager
            mock_session.post.return_value = mock_response
            MockSession.return_value = mock_session

            await api.authenticate()

            assert api._authenticated is True
            mock_session.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_failure(self, api: BboxApi) -> None:
        """Test authentication failure with 401 status."""
        with patch("aiobbox.client.ClientSession") as MockSession:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 401
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session.post.return_value = mock_response
            MockSession.return_value = mock_session

            with pytest.raises(BboxApiError):
                await api.authenticate()

    @pytest.mark.asyncio
    async def test_context_manager(self) -> None:
        """Test context manager usage."""
        with patch("aiobbox.client.ClientSession") as MockSession:
            mock_session = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.__aenter__ = AsyncMock(return_value=mock_response)
            mock_response.__aexit__ = AsyncMock(return_value=None)

            mock_session.post.return_value = mock_response
            MockSession.return_value = mock_session

            async with BboxApi("test_password") as api:
                assert api._authenticated is True

    @pytest.mark.asyncio
    async def test_get_router_info(
        self, api: BboxApi, sample_device_data: dict
    ) -> None:
        """Test getting device information."""
        api._authenticated = True
        api._session = AsyncMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [{"device": sample_device_data}]
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.raise_for_status = Mock()
        api._session.request.return_value = mock_response

        device = await api.get_router_info()

        assert device.modelname == "F@st5696b"
        assert device.status == 1
        api._session.request.assert_called_once_with(
            "GET",
            "https://mabbox.bytel.fr/api/v1/device",
            headers={
                "Referer": "https://mabbox.bytel.fr/api/v1/",
                "Origin": "https://mabbox.bytel.fr/api/v1",
            },
        )

    @pytest.mark.asyncio
    async def test_get_hosts(self, api: BboxApi, sample_host_data: dict) -> None:
        """Test getting connected hosts."""
        api._authenticated = True
        api._session = AsyncMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [{"hosts": {"list": [sample_host_data]}}]
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.raise_for_status = Mock()
        api._session.request.return_value = mock_response

        hosts = await api.get_hosts()

        assert len(hosts) == 1
        assert hosts[0].hostname == "test-device"
        assert hosts[0].informations.type == "Téléphone"
        api._session.request.assert_called_once_with(
            "GET",
            "https://mabbox.bytel.fr/api/v1/hosts",
            headers={
                "Referer": "https://mabbox.bytel.fr/api/v1/",
                "Origin": "https://mabbox.bytel.fr/api/v1",
            },
        )

    @pytest.mark.asyncio
    async def test_get_wan_ip_stats(
        self, api: BboxApi, sample_wan_stats_data: dict
    ) -> None:
        """Test getting WAN IP statistics."""
        api._authenticated = True
        api._session = AsyncMock()

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = [
            {"wan": {"ip": {"stats": sample_wan_stats_data}}}
        ]
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.raise_for_status = Mock()
        api._session.request.return_value = mock_response

        wan_stats = await api.get_wan_ip_stats()

        assert wan_stats.rx.bandwidth == 29
        assert wan_stats.tx.bandwidth == 10
        api._session.request.assert_called_once_with(
            "GET",
            "https://mabbox.bytel.fr/api/v1/wan/ip/stats",
            headers={
                "Referer": "https://mabbox.bytel.fr/api/v1/",
                "Origin": "https://mabbox.bytel.fr/api/v1",
            },
        )

    @pytest.mark.asyncio
    async def test_request_not_authenticated(self, api: BboxApi) -> None:
        """Test request without authentication."""
        with pytest.raises(BboxApiError, match="Not authenticated"):
            await api._request("GET", "device")

    @pytest.mark.asyncio
    async def test_request_session_expired(self, api: BboxApi) -> None:
        """Test request with expired session."""
        api._authenticated = True
        api._session = AsyncMock()

        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.__aenter__ = AsyncMock(return_value=mock_response)
        mock_response.__aexit__ = AsyncMock(return_value=None)
        mock_response.raise_for_status = Mock()
        api._session.request.return_value = mock_response

        with pytest.raises(BboxApiError, match="Session expired"):
            await api._request("GET", "device")

        assert api._authenticated is False

    @pytest.mark.asyncio
    async def test_close(self, api: BboxApi) -> None:
        """Test closing the session."""
        mock_session = AsyncMock()
        api._session = mock_session
        await api.close()

        mock_session.close.assert_called_once()
        # mypy sometimes incorrectly flags these as unreachable due to async mocking
        if api._session is not None:
            raise AssertionError("Session should be None after close")
        if api._authenticated:  # type: ignore[unreachable]
            raise AssertionError("Should not be authenticated after close")
