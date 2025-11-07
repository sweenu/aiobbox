"""Tests for Pydantic models."""

from typing import Any

import pytest
from pydantic import ValidationError

from aiobbox.models import Host, Router, WANIPStats, WANStats


class TestRouterModel:
    """Test suite for Router model."""

    def test_router_creation(self, sample_device_data: dict[str, Any]) -> None:
        """Test creating a Router instance from sample data."""
        router = Router(**sample_device_data["device"])
        assert router.modelname == "TestRouter3000"
        assert router.serialnumber == "123456789012345"
        assert router.numberofboots == 42
        assert router.uptime == 4043471
        assert router.using.ftth is True
        assert router.using.adsl is False

    def test_router_display(self, sample_device_data: dict[str, Any]) -> None:
        """Test router display settings."""
        router = Router(**sample_device_data["device"])
        assert router.display.luminosity == 2
        assert router.display.luminosity_extender == 100
        assert router.display.state == "."

    def test_router_versions(self, sample_device_data: dict[str, Any]) -> None:
        """Test router version information."""
        router = Router(**sample_device_data["device"])
        assert router.main.version == "1.0.0"
        assert router.running.version == "1.0.0"
        assert router.spl.version is None  # Empty string converted to None

    def test_router_empty_string_to_none(self) -> None:
        """Test that empty strings are converted to None."""
        data = {
            "now": "2025-11-07T13:40:00+0100",
            "status": 1,
            "numberofboots": 10,
            "modelname": "Test",
            "modelclass": "Test",
            "optimisation": 1,
            "user_configured": 1,
            "serialnumber": "123",
            "display": {"luminosity": 0, "luminosity_extender": 0, "state": "."},
            "main": {"version": ""},
            "reco": {"version": ""},
            "running": {"version": ""},
            "spl": {"version": ""},
            "tpl": {"version": ""},
            "ldr1": {"version": ""},
            "ldr2": {"version": ""},
            "firstusedate": "2024-06-01T08:00:00Z",
            "uptime": 0,
            "lastFactoryReset": 0,
            "using": {"ipv4": 1, "ipv6": 1, "ftth": 1, "adsl": 0, "vdsl": 0},
            "isCertified": 1,
        }

        router = Router(**data)
        assert router.main.version is None

    def test_router_missing_required_field(self) -> None:
        """Test that missing required fields raise ValidationError."""
        data = {
            "now": "2025-11-07T13:40:00+0100",
            "status": 1,
            "numberofboots": 10,
            "modelname": "Test",
            "modelclass": "Test",
            "optimisation": 1,
            "user_configured": 1,
            "serialnumber": "123",
            "display": {"luminosity": 0, "luminosity_extender": 0, "state": ""},
            # Missing: main, reco, running, spl, tpl, ldr1, ldr2
            "uptime": 0,
            "lastFactoryReset": 0,
            "using": {"ipv4": 1, "ipv6": 1, "ftth": 1, "adsl": 0, "vdsl": 0},
            "isCertified": 1,
        }

        with pytest.raises(ValidationError) as exc_info:
            Router(**data)
        # Verify it's actually a validation error with proper structure
        assert exc_info.value.error_count() >= 1


class TestHostModel:
    """Test suite for Host model."""

    @pytest.mark.parametrize(
        "host_fixture,expected_id,expected_active,expected_link,expected_hostname",
        [
            ("sample_inactive_host", 1, False, "Wifi 5", None),
            ("sample_active_dhcp_host", 5, True, "Wifi 2.4", "office-printer"),
            ("sample_ethernet_host", 10, True, "Ethernet", "home-server"),
        ],
    )
    def test_host_creation(
        self,
        request: pytest.FixtureRequest,
        host_fixture: str,
        expected_id: int,
        expected_active: bool,
        expected_link: str,
        expected_hostname: str | None,
    ) -> None:
        """Test creating Host instances with various connection types."""
        host_data = request.getfixturevalue(host_fixture)
        host = Host(**host_data)
        assert host.id == expected_id
        assert host.active is expected_active
        assert host.link == expected_link
        assert host.hostname == expected_hostname

    def test_active_dhcp_host_with_ipv6(
        self, sample_active_dhcp_host: dict[str, Any]
    ) -> None:
        """Test creating an active DHCP host with IPv6 addresses."""
        host = Host(**sample_active_dhcp_host)
        assert host.type == "DHCP"
        assert len(host.ip6address) == 2
        assert host.ip6address[0].ipaddress == "fe80::aabb:ccff:fedd:ee05"
        assert host.wireless is not None
        assert host.wireless.band == 2.4
        assert host.wireless.rssi0 == -52

    def test_ethernet_host_connectivity(
        self, sample_ethernet_host: dict[str, Any]
    ) -> None:
        """Test host connected via Ethernet with speed info."""
        host = Host(**sample_ethernet_host)
        assert host.me is True
        assert host.ethernet is not None
        assert host.ethernet.speed == 2500
        assert host.ethernet.mode == "Full"

    def test_host_wireless_by_band(
        self, sample_active_dhcp_host: dict[str, Any]
    ) -> None:
        """Test wireless per-band information."""
        host = Host(**sample_active_dhcp_host)
        assert len(host.wirelessByBand) == 1
        assert host.wirelessByBand[0].band == 2.4
        assert host.wirelessByBand[0].rate == 72


class TestWANStatsModel:
    """Test suite for WAN statistics models."""

    def test_wan_stats_creation(self, sample_wan_stats_data: dict[str, Any]) -> None:
        """Test creating WANIPStats instance."""
        stats = WANIPStats(**sample_wan_stats_data["wan"]["ip"]["stats"])
        assert stats.tx.packets == 400000
        assert stats.rx.packets == 500000

    def test_wan_stats_field_validation(self) -> None:
        """Test field validation for WANStats."""
        data = {
            "packets": 1000,
            "bytes": 500000,
            "packetserrors": 0,
            "packetsdiscards": 0,
            "occupation": 50,
            "bandwidth": 100,
            "maxBandwidth": 1000,
            "contractualBandwidth": 500,
        }

        stats = WANStats(**data)
        assert stats.packets == 1000
        assert stats.occupation == 50

    @pytest.mark.parametrize(
        "invalid_field,invalid_value,field_name",
        [
            ("occupation", 150, "occupation"),  # > 100
            ("packets", -100, "packets"),  # < 0
            ("bytes", -50, "bytes"),  # < 0
        ],
    )
    def test_wan_stats_invalid_field(
        self, invalid_field: str, invalid_value: int, field_name: str
    ) -> None:
        """Test that invalid field values raise ValidationError."""
        data = {
            "packets": 1000,
            "bytes": 500000,
            "packetserrors": 0,
            "packetsdiscards": 0,
            "occupation": 50,
            "bandwidth": 100,
            "maxBandwidth": 1000,
            "contractualBandwidth": 500,
        }
        data[invalid_field] = invalid_value

        with pytest.raises(ValidationError) as exc_info:
            WANStats(**data)

        errors = exc_info.value.errors()
        assert any(error["loc"][0] == field_name for error in errors)

    def test_wan_stats_missing_required_field(self) -> None:
        """Test that missing required fields raise ValidationError."""
        data = {
            "packets": 1000,
            # Missing: bytes, packetserrors, packetsdiscards, etc.
            "occupation": 50,
        }

        with pytest.raises(ValidationError) as exc_info:
            WANStats(**data)
        # Should have multiple validation errors for missing fields
        assert exc_info.value.error_count() >= 1
