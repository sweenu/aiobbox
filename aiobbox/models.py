"""Pydantic models for Bbox API responses."""

from datetime import datetime
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
)


def fix_mojibake(s: str) -> str:
    """Fix mojibake encoding issues from API responses.

    Args:
        s: String potentially containing mojibake

    Returns:
        Decoded string with fixed encoding
    """
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


CleanString = Annotated[str, AfterValidator(fix_mojibake)]


class CustomBaseModel(BaseModel):
    """Base model with custom validation for API responses."""

    model_config = ConfigDict(
        coerce_numbers_to_str=True,
        validate_assignment=True,
        str_strip_whitespace=True,
    )

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, data: Any) -> Any:
        """Convert empty strings to None across all fields.

        Args:
            data: Raw data from API

        Returns:
            Transformed data with empty strings converted to None
        """
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


### /device ###


class RouterDisplay(CustomBaseModel):
    """Router display settings."""

    luminosity: int = Field(ge=0, description="Display brightness level")
    luminosity_extender: int = Field(ge=0, description="Extender brightness level")
    state: str = Field(description="Current display state")


class RouterVersion(CustomBaseModel):
    """Router firmware version information."""

    version: str | None = Field(None, description="Version string")
    date: datetime | None = Field(None, description="Build date")


class RouterUsing(CustomBaseModel):
    """Router connection type flags."""

    ipv4: bool = Field(description="IPv4 enabled")
    ipv6: bool = Field(description="IPv6 enabled")
    ftth: bool = Field(description="Fiber connection")
    adsl: bool = Field(description="ADSL connection")
    vdsl: bool = Field(description="VDSL connection")


class Router(CustomBaseModel):
    """Router device information."""

    now: datetime = Field(description="Current router time")
    status: int = Field(description="Router status code")
    numberofboots: int = Field(ge=0, description="Number of reboots")
    modelname: CleanString = Field(description="Router model name")
    modelclass: str = Field(description="Router model class")
    optimisation: bool
    user_configured: bool
    serialnumber: str = Field(description="Device serial number")
    display: RouterDisplay
    main: RouterVersion
    reco: RouterVersion
    running: RouterVersion
    spl: RouterVersion
    tpl: RouterVersion
    ldr1: RouterVersion
    ldr2: RouterVersion
    firstusedate: datetime = Field(description="Timestamp of router's first use")
    uptime: int = Field(ge=0, description="Uptime in seconds")
    lastFactoryReset: int
    using: RouterUsing


### /hosts ###


class IPv6Address(CustomBaseModel):
    """IPv6 address information."""

    ipaddress: str = Field(description="IPv6 address")
    status: str = Field(description="Address status (Preferred, etc.)")
    lastseen: datetime = Field(description="Last seen timestamp")
    lastscan: datetime = Field(description="Last scan timestamp")


class EthernetInfo(CustomBaseModel):
    """Ethernet interface information."""

    physicalport: int = Field(description="Physical port number")
    logicalport: int = Field(description="Logical port number")
    speed: int = Field(ge=0, description="Connection speed in Mbps")
    mode: str | None = Field(None, description="Connection mode (Full, Half)")


class WirelessInfo(CustomBaseModel):
    """Wireless interface information."""

    wexindex: int = Field(description="Wireless extension index")
    static: bool = Field(description="Static configuration flag")
    band: int | float | None = Field(None, description="Frequency band (2.4, 5, 6)")
    txUsage: int = Field(ge=0, description="TX usage percentage")
    rxUsage: int = Field(ge=0, description="RX usage percentage")
    estimatedRate: int = Field(ge=0, description="Estimated rate")
    rssi0: int = Field(description="RSSI signal strength")
    mcs: int = Field(ge=0, description="Modulation Coding Scheme")
    rate: int = Field(ge=0, description="Data rate in Mbps")


class WirelessByBand(CustomBaseModel):
    """Wireless information per frequency band."""

    band: int | float = Field(description="Frequency band")
    txUsage: int = Field(ge=0, description="TX usage percentage")
    rxUsage: int = Field(ge=0, description="RX usage percentage")
    estimatedRate: int = Field(ge=0, description="Estimated rate")
    rssi0: int = Field(description="RSSI per band")
    mcs: int = Field(ge=0)
    rate: int = Field(ge=0)


class PLCInfo(CustomBaseModel):
    """PowerLine Communication interface information."""

    rxphyrate: str | None = Field(None, description="RX physical rate")
    txphyrate: str | None = Field(None, description="TX physical rate")
    associateddevice: int = Field(description="Associated device count")
    interface: int = Field(description="Interface index")
    ethernetspeed: int = Field(ge=0, description="Ethernet speed")


class DeviceInformation(CustomBaseModel):
    """Device information and metadata."""

    type: CleanString = Field(description="Device type")
    manufacturer: CleanString | None = Field(None, description="Manufacturer")
    model: CleanString | None = Field(None, description="Device model")
    icon: str = Field(description="Icon identifier")
    operatingSystem: CleanString | None = Field(None, description="OS type")
    version: CleanString | None = Field(None, description="OS version")


class ParentalControl(CustomBaseModel):
    """Parental control settings."""

    enable: bool = Field(description="Enabled flag")
    status: str = Field(description="Current status")
    statusRemaining: int = Field(ge=0, description="Status remaining time")
    statusUntil: datetime | None = Field(None, description="Until timestamp")


class PingInfo(CustomBaseModel):
    """Ping statistics."""

    average: int | float = Field(ge=0, description="Average ping time")


class ScanInfo(CustomBaseModel):
    """Network scan information."""

    services: list[Any] = Field(default_factory=list, description="Services discovered")


class Host(CustomBaseModel):
    """Network host/device information."""

    id: int = Field(description="Unique host ID")
    active: bool = Field(description="Currently active flag")
    hostname: CleanString | None = Field(None, description="Device hostname")
    ipaddress: str = Field(description="IPv4 address")
    macaddress: str = Field(description="MAC address")
    type: str = Field(description="Connection type (DHCP, Static)")
    link: str = Field(description="Link type (Wifi 2.4, Wifi 5, Wifi 6, Ethernet)")
    lease: int = Field(description="DHCP lease time remaining in seconds")
    firstseen: datetime = Field(description="First seen timestamp")
    lastseen: int = Field(description="Seconds since last seen")
    devicetype: str | None = Field(None, description="Device type classification")
    duid: str | None = Field(None, description="DHCP unique identifier")
    guest: bool = Field(default=False, description="Guest network flag")
    serialNumber: str | None = Field(None, description="Device serial number")
    ip6address: list[IPv6Address] = Field(
        default_factory=list, description="IPv6 addresses"
    )
    ethernet: EthernetInfo | None = Field(None, description="Ethernet interface info")
    wireless: WirelessInfo | None = Field(None, description="Wireless interface info")
    wirelessByBand: list[WirelessByBand] = Field(
        default_factory=list, description="Wireless info per band"
    )
    plc: PLCInfo | None = Field(None, description="PLC interface info")
    informations: DeviceInformation | None = Field(
        None, description="Device information"
    )
    parentalcontrol: ParentalControl | None = Field(
        None, description="Parental control settings"
    )
    ping: PingInfo | None = Field(None, description="Ping statistics")
    scan: ScanInfo | None = Field(None, description="Network scan info")
    me: bool = Field(default=False, description="This device flag (router itself)")


### /wan/ip/stats ###


class WANStats(CustomBaseModel):
    """WAN interface statistics."""

    packets: int = Field(ge=0, description="Total packets transmitted")
    bytes: int = Field(ge=0, description="Total bytes transmitted")
    packetserrors: int = Field(ge=0, description="Packet errors")
    packetsdiscards: int = Field(ge=0, description="Packets discarded")
    occupation: int = Field(ge=0, le=100, description="Bandwidth occupation percentage")
    bandwidth: int = Field(ge=0, description="Current bandwidth usage")
    maxBandwidth: int = Field(ge=0, description="Maximum bandwidth")
    contractualBandwidth: int = Field(ge=0, description="Contractual bandwidth")


class WANIPStats(CustomBaseModel):
    """WAN IP interface statistics."""

    rx: WANStats
    tx: WANStats
