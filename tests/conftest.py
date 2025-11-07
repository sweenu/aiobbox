"""Shared pytest fixtures for aiobbox tests."""

from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import aiohttp
import pytest

# Type alias for the mock response factory
MockResponseFactory = Callable[[Any, int, bool], MagicMock]


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture providing a mocked aiohttp session."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_response_factory() -> MockResponseFactory:
    """Factory fixture for creating mock async response context managers.

    This factory simplifies creation of mock responses for testing API calls.
    It handles the complexity of async context managers internally.
    """

    def _create(
        return_value: Any = None, status: int = 200, raise_for_status: bool = False
    ) -> MagicMock:
        """Create a mock response and its async context manager.

        Args:
            return_value: JSON response data
            status: HTTP status code
            raise_for_status: Whether to raise for status errors

        Returns:
            Mock context manager for session.request() calls
        """
        mock_response = AsyncMock()
        mock_response.status = status
        mock_response.json = AsyncMock(return_value=return_value)

        if raise_for_status:
            mock_response.raise_for_status = MagicMock(
                side_effect=aiohttp.ClientResponseError(
                    request_info=MagicMock(),
                    history=(),
                    status=status,
                )
            )
        else:
            mock_response.raise_for_status = MagicMock()

        context = MagicMock()
        context.__aenter__ = AsyncMock(return_value=mock_response)
        context.__aexit__ = AsyncMock(return_value=None)
        return context

    return _create


@pytest.fixture
def sample_device_data() -> dict[str, Any]:
    """Fixture providing sample device data from /device endpoint."""
    return {
        "device": {
            "now": "2025-11-07T13:40:00+0100",
            "status": 1,
            "numberofboots": 42,
            "modelname": "TestRouter3000",
            "modelclass": "TR3000",
            "optimisation": 1,
            "user_configured": 1,
            "serialnumber": "123456789012345",
            "display": {
                "luminosity": 2,
                "luminosity_extender": 100,
                "state": ".",
            },
            "main": {"version": "1.0.0", "date": "2025-01-15T10:00:00Z"},
            "reco": {"version": "1.0.0", "date": "2025-01-15T09:30:00Z"},
            "running": {
                "version": "1.0.0",
                "date": "2025-01-15T09:45:00Z",
            },
            "spl": {"version": ""},
            "tpl": {"version": ""},
            "ldr1": {"version": "2.1.0"},
            "ldr2": {"version": "2.1.0"},
            "firstusedate": "2024-06-01T08:00:00Z",
            "uptime": 4043471,
            "lastFactoryReset": 0,
            "using": {"ipv4": 1, "ipv6": 1, "ftth": 1, "adsl": 0, "vdsl": 0},
            "isCertified": 1,
        }
    }


@pytest.fixture
def sample_inactive_host() -> dict[str, Any]:
    """Fixture providing sample inactive host (Static IP, WiFi)."""
    return {
        "id": 1,
        "active": 0,
        "hostname": "",
        "ipaddress": "192.168.1.100",
        "macaddress": "aa:bb:cc:dd:ee:01",
        "type": "Static",
        "link": "Wifi 5",
        "lease": 0,
        "firstseen": "2024-06-15T10:00:00+0200",
        "lastseen": 3131260,
        "devicetype": "Device",
        "duid": "",
        "guest": 0,
        "serialNumber": "",
        "ip6address": [],
        "ethernet": {"physicalport": 0, "logicalport": 0, "speed": 0, "mode": ""},
        "wireless": {
            "wexindex": 0,
            "static": 0,
            "band": "",
            "txUsage": 0,
            "rxUsage": 0,
            "estimatedRate": 0,
            "rssi0": 0,
            "mcs": 0,
            "rate": 0,
        },
        "wirelessByBand": [],
        "plc": {
            "rxphyrate": "",
            "txphyrate": "",
            "associateddevice": 0,
            "interface": 0,
            "ethernetspeed": 0,
        },
        "informations": {
            "type": "GÃ©nÃ©rique",  # mobajike
            "manufacturer": "GenericCorp",
            "model": "Device",
            "icon": "generic",
            "operatingSystem": "Unknown OS",
            "version": "",
        },
        "parentalcontrol": {
            "enable": 0,
            "status": "Allowed",
            "statusRemaining": 0,
            "statusUntil": "",
        },
        "ping": {"average": 0},
        "scan": {"services": []},
    }


@pytest.fixture
def sample_active_dhcp_host() -> dict[str, Any]:
    """Fixture providing sample active host (DHCP, WiFi 2.4, IPv6)."""
    return {
        "id": 5,
        "active": 1,
        "hostname": "office-printer",
        "ipaddress": "192.168.1.110",
        "macaddress": "aa:bb:cc:dd:ee:05",
        "type": "DHCP",
        "link": "Wifi 2.4",
        "lease": 67189,
        "firstseen": "2024-06-01T12:30:00+0200",
        "lastseen": 0,
        "devicetype": "Device",
        "duid": "02:00:00:00:00:03:00:01:aa:bb:cc:dd:ee:05",
        "guest": 0,
        "serialNumber": "",
        "ip6address": [
            {
                "ipaddress": "fe80::aabb:ccff:fedd:ee05",
                "status": "Preferred",
                "lastseen": "2025-11-07T07:17:15+0100",
                "lastscan": "2025-10-31T10:16:40+0100",
            },
            {
                "ipaddress": "2001:db8:85a3::8a2e:370:7334",
                "status": "Preferred",
                "lastseen": "2025-11-01T20:13:42+0100",
                "lastscan": "1970-01-16T07:15:14+0100",
            },
        ],
        "ethernet": {"physicalport": 10, "logicalport": 11, "speed": 0, "mode": ""},
        "wireless": {
            "wexindex": 0,
            "static": 0,
            "band": "2.4",
            "txUsage": 0,
            "rxUsage": 0,
            "estimatedRate": 30,
            "rssi0": "-52",
            "mcs": 7,
            "rate": 72,
        },
        "wirelessByBand": [
            {
                "band": "2.4",
                "txUsage": 0,
                "rxUsage": 0,
                "estimatedRate": 30,
                "rssi0": "-52",
                "mcs": 7,
                "rate": 72,
            }
        ],
        "plc": {
            "rxphyrate": "",
            "txphyrate": "",
            "associateddevice": 0,
            "interface": 0,
            "ethernetspeed": 0,
        },
        "informations": {
            "type": "Printer",
            "manufacturer": "PrinterVendor",
            "model": "OfficeNet 5000",
            "icon": "printer",
            "operatingSystem": "Embedded OS",
            "version": "",
        },
        "parentalcontrol": {
            "enable": 0,
            "status": "Allowed",
            "statusRemaining": 0,
            "statusUntil": "",
        },
        "ping": {"average": 0},
        "scan": {"services": []},
    }


@pytest.fixture
def sample_ethernet_host() -> dict[str, Any]:
    """Fixture providing sample host connected via Ethernet."""
    return {
        "id": 10,
        "me": 1,
        "active": 1,
        "hostname": "home-server",
        "ipaddress": "192.168.1.50",
        "macaddress": "aa:bb:cc:dd:ee:10",
        "type": "DHCP",
        "link": "Ethernet",
        "lease": 61613,
        "firstseen": "2024-08-10T14:20:00+0200",
        "lastseen": 0,
        "devicetype": "Device",
        "duid": "e3:a1:b5:37:00:02:00:00:ab:11:6d:a8:bb:63:72:7d:94:e4",
        "guest": 0,
        "serialNumber": "",
        "ip6address": [
            {
                "ipaddress": "fe80::aabb:ccff:fedd:ee10",
                "status": "Preferred",
                "lastseen": "2025-11-07T13:39:38+0100",
                "lastscan": "2025-09-25T14:38:44+0200",
            },
            {
                "ipaddress": "2001:db8:85a3::8a2e:370:7335",
                "status": "Preferred",
                "lastseen": "2025-10-24T23:14:32+0200",
                "lastscan": "1970-01-16T07:15:14+0100",
            },
        ],
        "ethernet": {
            "physicalport": 2,
            "logicalport": 3,
            "speed": 2500,
            "mode": "Full",
        },
        "wireless": {
            "wexindex": 0,
            "static": 0,
            "band": "",
            "txUsage": 0,
            "rxUsage": 0,
            "estimatedRate": 0,
            "rssi0": 0,
            "mcs": 0,
            "rate": 0,
        },
        "wirelessByBand": [],
        "plc": {
            "rxphyrate": "",
            "txphyrate": "",
            "associateddevice": 0,
            "interface": 0,
            "ethernetspeed": 0,
        },
        "informations": {
            "type": "Generic Device",
            "manufacturer": "ServerVendor",
            "model": "EdgeNode Pro",
            "icon": "generic",
            "operatingSystem": "Linux",
            "version": "",
        },
        "parentalcontrol": {
            "enable": 0,
            "status": "Allowed",
            "statusRemaining": 0,
            "statusUntil": "",
        },
        "ping": {"average": 0},
        "scan": {"services": []},
    }


@pytest.fixture
def sample_hosts_list(
    sample_inactive_host: dict[str, Any],
    sample_active_dhcp_host: dict[str, Any],
    sample_ethernet_host: dict[str, Any],
) -> dict[str, Any]:
    """Fixture providing a list of sample hosts."""
    return {
        "hosts": {
            "list": [
                sample_inactive_host,
                sample_active_dhcp_host,
                sample_ethernet_host,
            ]
        }
    }


@pytest.fixture
def sample_wan_stats_data() -> dict[str, Any]:
    """Fixture providing sample WAN stats data from /wan/ip/stats endpoint."""
    return {
        "wan": {
            "ip": {
                "stats": {
                    "tx": {
                        "packets": 400000,
                        "bytes": 2400000,
                        "packetserrors": 5,
                        "packetsdiscards": 2,
                        "occupation": 25,
                        "bandwidth": 250,
                        "maxBandwidth": 1000,
                        "contractualBandwidth": 500,
                    },
                    "rx": {
                        "packets": 500000,
                        "bytes": 2500000,
                        "packetserrors": 5,
                        "packetsdiscards": 3,
                        "occupation": 20,
                        "bandwidth": 200,
                        "maxBandwidth": 1000,
                        "contractualBandwidth": 500,
                    },
                }
            }
        }
    }
