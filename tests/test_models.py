from datetime import datetime

import pytest

from aiobbox.models import Host, Router, WANIPStats, WANStats


class TestModels:
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
        """Fixture providing complete sample host data."""
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
                "type": "computer",
                "manufacturer": "Test Manufacturer",
                "model": "Test Model",
                "icon": "computer",
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

    def test_device_model(self, sample_device_data: dict) -> None:
        """Test Device model with example data."""
        device = Router(**sample_device_data)  # type: ignore[arg-type]

        assert device.modelname == "F@st5696b"
        assert device.serialnumber == "123456789012345"
        assert device.status == 1
        assert device.uptime == 404347
        assert isinstance(device.now, datetime)
        assert device.using.ipv4 == 1
        assert device.using.ftth == 1

    def test_host_model(self, sample_host_data: dict) -> None:
        """Test Host model with complete data."""
        host = Host(**sample_host_data)  # type: ignore[arg-type]

        assert host.id == 1
        assert host.active == 1
        assert host.macaddress == "aa:bb:cc:dd:ee:ff"
        assert host.hostname == "test-device"
        assert host.ipaddress == "192.168.1.100"
        assert host.duid == "test-duid"
        assert host.serialNumber is None  # Empty string converted to None

    def test_wan_stats_model(self, sample_wan_stats_data: dict) -> None:
        """Test WAN stats model with example data."""
        wan_stats = WANIPStats(**sample_wan_stats_data)  # type: ignore[arg-type]

        assert wan_stats.rx.bandwidth == 29
        assert wan_stats.tx.bandwidth == 10
        assert wan_stats.rx.packets == 104522008
        assert wan_stats.tx.packets == 11135558
        assert wan_stats.rx.bytes == 130580798930
        assert wan_stats.tx.bytes == 5471690248

    def test_hosts_list_minimal(self, sample_host_data: dict) -> None:
        """Test Host model with minimal data for list usage."""
        # Create minimal version by removing optional fields
        minimal_data = sample_host_data.copy()
        minimal_data["hostname"] = ""

        host = Host(**minimal_data)  # type: ignore[arg-type]

        assert host.id == 1
        assert host.active == 1
        assert host.macaddress == "aa:bb:cc:dd:ee:ff"
        assert host.type == "wireless"
        assert host.hostname is None  # Empty string converted to None
        assert host.duid == "test-duid"
        assert host.serialNumber is None  # Empty string converted to None

    def test_device_with_empty_strings_converted_to_none(
        self, sample_device_data: dict
    ) -> None:
        """Test Device model handles empty strings converted to None."""
        device = Router(**sample_device_data)  # type: ignore[arg-type]

        # Check that empty strings were converted to None
        assert device.spl.version is None
        assert device.tpl.version is None

        # Check that non-empty strings remain as strings
        assert device.modelname == "F@st5696b"
        assert device.main.version == "25.5.28"
        assert device.ldr1.version == "4.4.20"

    def test_wan_stats_validation(self) -> None:
        """Test WANStats validation."""
        stats_data = {
            "packets": 100,
            "bytes": 1000,
            "packetserrors": 0,
            "packetsdiscards": 0,
            "occupation": 0,
            "bandwidth": 10,
            "maxBandwidth": 100,
            "contractualBandwidth": 50,
        }

        stats = WANStats(**stats_data)  # type: ignore[arg-type]
        assert stats.packets == 100
        assert stats.bytes == 1000
        assert stats.bandwidth == 10

    def test_empty_string_to_none_conversion(self) -> None:
        """Test that empty strings are converted to None by model_validator."""
        device_data = {
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

        device = Router(**device_data)  # type: ignore[arg-type]

        # Check that empty strings were converted to None
        assert device.spl.version is None
        assert device.tpl.version is None

        # Check that non-empty strings remain as strings
        assert device.modelname == "F@st5696b"
        assert device.main.version == "25.5.28"
        assert device.ldr1.version == "4.4.20"
