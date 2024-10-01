from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json

from .enums import ParamModulation, ParamDR, ParamSel, ParamSession, \
    ParamTarget, AntiCollisionMode, ParamSelectAction, ParamSelectTarget, ParamMemory, Region, ParamFhLbtMode


@dataclass_json
@dataclass
class ArgumentsReaderInformationDetail:
    region: Region = None
    channel: int = None
    read_time: int = None
    idle_time: int = None
    cw_sense_time: int = None
    lbt_rf_level: float = None
    current_tx_power: float = None
    min_tx_power: float = None
    max_tx_power: float = None
    BLF: int = None
    modulation: ParamModulation = None
    DR: ParamDR = None


@dataclass_json
@dataclass
class ArgumentsCurrentRfChannel:
    channel: int = None
    offset: int = None


@dataclass_json
@dataclass
class ArgumentsFrequencyHoppingTable:
    size: int = None
    channels: List[int] = None


@dataclass_json
@dataclass
class ArgumentsAntiCollisionMode:
    mode: AntiCollisionMode = None
    initial_q: int = None
    max_q: int = None
    min_q: int = None


@dataclass_json
@dataclass
class ArgumentsModulationMode:
    BLF: int = None
    modulation: ParamModulation = None
    DR: ParamDR = None


@dataclass_json
@dataclass
class ArgumentsQueryParameters:
    DR: ParamDR = None
    modulation: ParamModulation = None
    pilot_tone: bool = None
    sel: ParamSel = None
    session: ParamSession = None
    target: ParamTarget = None
    target_toggle: bool = None
    q: int = None


@dataclass_json
@dataclass
class ArgumentsSelectFilter:
    index: int = None
    target: ParamSelectTarget = None
    action: ParamSelectAction = None
    memory: ParamMemory = None
    pointer: int = None
    length: int = None
    mask: bytearray = None


@dataclass_json
@dataclass
class ArgumentsFhLbtParameters:
    dwell_time: int = None
    idle_time: int = None
    sense_time: int = None
    lbt_rf_level: int = None
    fh_lbt_mode: ParamFhLbtMode = None


@dataclass_json
@dataclass
class NotificationTpeCuiii:
    pc: bytearray = None
    epc: bytearray = None


@dataclass_json
@dataclass
class NotificationTpeCuiiiRssi(NotificationTpeCuiii):
    rssi: bytearray = None


@dataclass_json
@dataclass
class NotificationTpeCuiiiTid(NotificationTpeCuiii):
    tid: bytearray = None
