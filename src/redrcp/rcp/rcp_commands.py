import struct

from ..rcp.enums import ReaderInfoType, MessageType, MessageCode, TagType, Region, AntiCollisionMode, \
    ParamDR, ParamSel, ParamModulation, ParamSession, ParamTarget, ParamMemory, ParamFhLbtMode, ParamSelectTarget, \
    ParamSelectAction
from ..rcp.message_helper import buildCommand


def sw_reset():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_SYSTEM_RESET)
    return command


def get_registry_item(register):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_REGISTRY_ITEM,
                                      register >> 8, register & 0xFF)
    return command


def get_info(info_type: ReaderInfoType):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_READER_INFORMATION,
                                      info_type.value)
    return command


def get_current_rf_channel():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_CURRENT_RF_CHANNEL)
    return command


def get_frequency_hopping_table():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_FREQUENCY_HOPPING_TABLE)
    return command


def get_anti_collision_mode():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_ANTI_COLLISION_MODE)
    return command


def set_anti_collision_mode(anti_collision_mode: AntiCollisionMode, start_q, max_q, min_q):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_ANTI_COLLISION_MODE,
                                      anti_collision_mode.value, start_q, max_q, min_q)
    return command


def get_modulation_mode():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_MODULATION)
    return command


def set_modulation_mode(blf, modulation: ParamModulation, dr: ParamDR):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_MODULATION,
                                      0xFF,
                                      struct.pack('>H', int(blf)),
                                      modulation.value,
                                      dr.value)
    return command


def get_query_parameters():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_TYPE_QUERY_RELATED_PARAMETERS)
    return command


def set_query_parameters(dr: ParamDR, modulation: ParamModulation, pilot_tone: bool, sel: ParamSel,
                         session: ParamSession, target: ParamTarget, target_toggle: bool, q: int):
    payload_msb = (dr.value << 7) + (modulation.value << 5) + (pilot_tone << 4) + (sel.value << 2) + session.value
    payload_lsb = (target.value << 7) + target_toggle + (q << 3)
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_TYPE_QUERY_RELATED_PARAMETERS,
                                      payload_msb, payload_lsb)
    return command


def get_selection_filter(idx: int):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_SELECTION_FILTER,
                                      idx)
    return command


def set_selection_filter(idx: int, target: ParamSelectTarget, action: ParamSelectAction, memory: ParamMemory,
                         pointer_bit: int, length_bit: int, mask: bytearray):
    if length_bit > 0:
        command: bytearray = buildCommand(MessageType.COMMAND,
                                          MessageCode.SET_SELECTION_FILTER,
                                          idx, target, action, memory,
                                          struct.pack('>H', int(pointer_bit)), length_bit, mask)
    else:
        command: bytearray = buildCommand(MessageType.COMMAND,
                                          MessageCode.SET_SELECTION_FILTER,
                                          idx, target, action, memory,
                                          struct.pack('>H', int(pointer_bit)), 0)
    return command


def get_selection_enables():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_SELECTION_ENABLES)
    return command


def set_selection_enables(enable_mask):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_SELECTION_ENABLES,
                                      enable_mask)
    return command


def get_region():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_REGION)
    return command


def set_region(region: Region):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_REGION,
                                      region.value)
    return command


def get_tx_power():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_TX_POWER)
    return command


def set_tx_power(dbm):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_TX_POWER,
                                      struct.pack('>H', int(dbm * 10)))
    return command


def get_fh_lbt_parameters():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_FH_LBT_PARAMETERS)
    return command


def set_fh_lbt_parameters(dwell_time, idle_time, sense_time, lbt_rf_level, fh_lbt_mode: ParamFhLbtMode):
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.SET_FH_LBT_PARAMETERS,
                                      struct.pack('>H', dwell_time),
                                      struct.pack('>H', idle_time),
                                      struct.pack('>H', sense_time),
                                      struct.pack('>h', lbt_rf_level * 10),
                                      struct.pack('>H', fh_lbt_mode.value))
    return command


def get_rssi():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.GET_RSSI)
    return command


def set_cw(enable: bool):
    if enable:
        control = 0xFF
    else:
        control = 0x00
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.RF_CW_SIGNAL_CONTROL,
                                      control)
    return command


def read(epc, target_memory: ParamMemory, word_pointer, word_count=1, access_password=bytearray([0, 0, 0, 0])):
    if isinstance(epc, str):
        epc = bytearray.fromhex(epc)
    if access_password is None:
        access_password = bytearray([0, 0, 0, 0])
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.READ_TPE_C_TAG_DATA,
                                      access_password,
                                      struct.pack('>H', len(epc)),
                                      epc,
                                      target_memory.value,
                                      struct.pack('>H', word_pointer),
                                      struct.pack('>H', word_count))
    return command


def write(epc, target_memory: ParamMemory, word_pointer, data, access_password=bytearray([0, 0, 0, 0])):
    if isinstance(epc, str):
        epc = bytearray.fromhex(epc)
    if access_password is None:
        access_password = bytearray([0, 0, 0, 0])

    if isinstance(data, int):
        data_bytes = struct.pack('>H', data)
    elif isinstance(data, bytearray):
        data_bytes = data
    elif isinstance(data, str):
        data_bytes = bytearray.fromhex(data)
    elif isinstance(data, list):
        data_bytes = bytearray()
        for item in data:
            if isinstance(item, int):
                data_bytes.append(item)

    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.WRITE_TYPE_C_TAG_DATA,
                                      access_password,
                                      struct.pack('>H', len(epc)),
                                      epc,
                                      target_memory.value,
                                      struct.pack('>H', word_pointer),
                                      struct.pack('>H', int(len(data_bytes) / 2)),
                                      data_bytes)
    return command


def start_auto_read2(tag_type: TagType = TagType.TYPE_C, max_n_tags: int = 0, max_time_secs: int = 0,
                     repeat_cycle: int = 0):
    rc_msb = struct.pack('>H', repeat_cycle)[0]
    rc_lsb = struct.pack('>H', repeat_cycle)[1]
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.START_AUTO_READ2,
                                      tag_type.value, max_n_tags, max_time_secs, rc_msb, rc_lsb)
    return command


def stop_auto_read2():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.STOP_AUTO_READ2)
    return command


def start_auto_read_rssi(tag_type: TagType = TagType.TYPE_C, max_n_tags=0, max_time_secs=0, repeat_cycle=0):
    rc_msb = struct.pack('>H', repeat_cycle)[0]
    rc_lsb = struct.pack('>H', repeat_cycle)[1]
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.START_AUTO_READ_RSSI,
                                      tag_type.value, max_n_tags, max_time_secs, rc_msb, rc_lsb)
    return command


def stop_auto_read_rssi():
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.STOP_AUTO_READ_RSSI)
    return command


def start_auto_read_tid(max_n_tags=0, max_time_secs=0, repeat_cycle=0):
    rc_msb = struct.pack('>H', repeat_cycle)[0]
    rc_lsb = struct.pack('>H', repeat_cycle)[1]
    command: bytearray = buildCommand(MessageType.COMMAND,
                                      MessageCode.READ_TPE_CUIII_TID,
                                      max_n_tags, max_time_secs, rc_msb, rc_lsb)
    return command


def stop_auto_read_tid():
    return stop_auto_read2()
