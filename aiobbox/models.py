from datetime import datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator


def fix_mojibake(s: str) -> str:
    try:
        return s.encode("latin-1").decode("utf-8")
    except (UnicodeDecodeError, UnicodeEncodeError):
        return s


CleanString = Annotated[str, AfterValidator(fix_mojibake)]


class CustomBaseModel(BaseModel):
    model_config = ConfigDict(coerce_numbers_to_str=True)

    @model_validator(mode="before")
    @classmethod
    def empty_str_to_none(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {k: (None if v == "" else v) for k, v in data.items()}
        return data


### /device ###
class RouterDisplay(CustomBaseModel):
    luminosity: int
    luminosity_extender: int
    state: str


class RouterVersion(CustomBaseModel):
    version: str | None = None
    date: datetime | None = None


class RouterUsing(CustomBaseModel):
    ipv4: bool
    ipv6: bool
    ftth: bool
    adsl: bool
    vdsl: bool


class Router(CustomBaseModel):
    now: datetime
    status: int
    numberofboots: int
    modelname: str
    modelclass: str
    optimisation: bool
    user_configured: bool
    serialnumber: str
    display: RouterDisplay | None = None
    main: RouterVersion
    reco: RouterVersion
    running: RouterVersion
    spl: RouterVersion
    tpl: RouterVersion
    ldr1: RouterVersion
    ldr2: RouterVersion
    firstusedate: datetime
    uptime: int
    lastFactoryReset: int
    using: RouterUsing
    isCellularEnable: bool
    newihm: bool
    newihmCdc: bool


### /wan/ip/stats ###
class WANStats(CustomBaseModel):
    packets: int
    bytes: int
    packetserrors: int
    packetsdiscards: int
    occupation: int
    bandwidth: int
    maxBandwidth: int
    contractualBandwidth: int


class WANIPStats(CustomBaseModel):
    rx: WANStats
    tx: WANStats


### /hosts ###
class IP6Address(CustomBaseModel):
    ipaddress: str
    status: str
    lastseen: datetime
    lastscan: datetime


class EthernetInfo(CustomBaseModel):
    physicalport: int
    logicalport: int
    speed: int
    mode: str | None = None


class WirelessInfo(CustomBaseModel):
    wexindex: int
    static: int
    band: str | None = None
    txUsage: int
    rxUsage: int
    estimatedRate: int
    rssi0: int
    mcs: int
    rate: int


class WirelessByBand(CustomBaseModel):
    band: str
    txUsage: int
    rxUsage: int
    estimatedRate: int
    rssi0: int
    mcs: int
    rate: int


class PLCInfo(CustomBaseModel):
    rxphyrate: str | None = None
    txphyrate: str | None = None
    associateddevice: int
    interface: int
    ethernetspeed: int


class DeviceInfo(CustomBaseModel):
    type: CleanString
    manufacturer: str | None = None
    model: str | None = None
    icon: str
    operatingSystem: str | None = None
    version: str | None = None


class ParentalControl(CustomBaseModel):
    enable: bool
    status: str
    statusRemaining: int
    statusUntil: int | None = None


class PingInfo(CustomBaseModel):
    average: int


class ScanInfo(CustomBaseModel):
    services: list[str] | None = None


class Host(CustomBaseModel):
    id: int
    active: bool
    devicetype: str
    duid: str | None = None
    guest: bool
    hostname: str | None = None
    ipaddress: str
    lease: int
    link: str
    macaddress: str
    type: str
    firstseen: datetime
    lastseen: int
    serialNumber: str | None = None
    ip6address: list[IP6Address] | None = None
    ethernet: EthernetInfo
    wireless: WirelessInfo
    wirelessByBand: list[WirelessByBand]
    plc: PLCInfo
    informations: DeviceInfo
    parentalcontrol: ParentalControl
    ping: PingInfo
    scan: ScanInfo
