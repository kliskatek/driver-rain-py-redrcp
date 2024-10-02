import inspect
import logging
import time
from threading import Thread
from typing import Callable, List

from .rcp import rcp_commands
from .rcp.enums import ParamFhLbtMode, Region, ParamSelectTarget, ParamSelectAction, ParamMemory, \
    ParamDR, ParamModulation, ParamSel, ParamTarget, ParamSession, AntiCollisionMode, ReaderInfoType, TagType, \
    OperationResult
from .rcp.error_messages import ErrorMessage
from .rcp.message_arguments import ArgumentsReaderInformationDetail, NotificationTpeCuiiiTid, NotificationTpeCuiii, \
    NotificationTpeCuiiiRssi, ArgumentsCurrentRfChannel, ArgumentsFrequencyHoppingTable, ArgumentsAntiCollisionMode, \
    ArgumentsModulationMode, ArgumentsQueryParameters, ArgumentsSelectFilter, ArgumentsFhLbtParameters
from .rcp.rcp_rx_handler import RcpRxHandler
from .transport.serial import SerialPort

logger = logging.getLogger(__name__)


class RedRcp:
    def __init__(self):
        self.transport = SerialPort()
        self.RX_thread = Thread(target=self._rx_thread, daemon=True, name='RxThread')
        self.RX_thread_run = True
        self.RX_thread.start()
        self.rcp_rx_handler = RcpRxHandler()

    def set_notification_callback(self, notification_callback: Callable[[NotificationTpeCuiii |
                                                                         NotificationTpeCuiiiRssi |
                                                                         NotificationTpeCuiiiTid], None]):
        self.rcp_rx_handler.set_notification_callback(notification_callback)

    def connect(self, connection_string) -> bool:
        return self.transport.connect(connection_string)

    def is_connected(self) -> bool:
        return self.transport.is_connected()

    def disconnect(self) -> bool:
        if not self.is_connected():
            logger.info('RedRcp already disconnected.')
            return True
        try:
            self.RX_thread_run = False
            self.RX_thread.join()
            self.transport.disconnect()
            logger.info('RedRcp successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def _rx_thread(self):
        while self.RX_thread_run:
            if self.transport.is_connected():
                data = self.transport.read()
                if data is not None:
                    if len(data) > 0:
                        logger.debug('RX << ' + str(data.hex(sep=' ').upper()))
                        self.rcp_rx_handler.append_data(data)
            time.sleep(0.001)

    def _txrx_cmd(self, command: bytearray, name: str):
        if not self.transport.is_connected():
            logger.info('RedRcp is disconnected.')
            return None

        logger.info('TX -> ' + name)
        self.transport.write(command)
        logger.debug('TX >> ' + str(command.hex(sep=' ').upper()))
        try:
            response = self.rcp_rx_handler.get_response()
            logger.info('RX <- ' + str(response))
            return response
        except TimeoutError:
            logger.info('Timeout executing ' + name)
            return None

    def get_info_model(self) -> str | None:
        command: bytearray = rcp_commands.get_info(ReaderInfoType.MODEL)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_info_fw_version(self) -> str | None:
        command: bytearray = rcp_commands.get_info(ReaderInfoType.FW_VERSION)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_info_manufacturer(self) -> str | None:
        command: bytearray = rcp_commands.get_info(ReaderInfoType.MANUFACTURER)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_info_detail(self) -> ArgumentsReaderInformationDetail | None:
        command: bytearray = rcp_commands.get_info(ReaderInfoType.DETAIL)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_current_rf_channel(self) -> ArgumentsCurrentRfChannel | None:
        command: bytearray = rcp_commands.get_current_rf_channel()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_frequency_hopping_table(self) -> ArgumentsFrequencyHoppingTable | None:
        command: bytearray = rcp_commands.get_frequency_hopping_table()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_anti_collision_mode(self) -> ArgumentsAntiCollisionMode | None:
        command: bytearray = rcp_commands.get_anti_collision_mode()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_anti_collision_mode(self, anti_collision_mode: AntiCollisionMode,
                                start_q: int, max_q: int, min_q: int) -> OperationResult:
        command: bytearray = rcp_commands.set_anti_collision_mode(anti_collision_mode, start_q, max_q, min_q)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_modulation_mode(self) -> ArgumentsModulationMode | None:
        command: bytearray = rcp_commands.get_modulation_mode()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_modulation_mode(self, blf: int, modulation: ParamModulation, dr: ParamDR) -> OperationResult:
        command: bytearray = rcp_commands.set_modulation_mode(blf, modulation, dr)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_query_parameters(self) -> ArgumentsQueryParameters | None:
        command: bytearray = rcp_commands.get_query_parameters()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_query_parameters(self, dr: ParamDR, modulation: ParamModulation, pilot_tone: bool, sel: ParamSel,
                             session: ParamSession, target: ParamTarget, target_toggle: bool,
                             q: int) -> OperationResult:
        command: bytearray = rcp_commands.set_query_parameters(dr, modulation, pilot_tone, sel, session, target,
                                                               target_toggle, q)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_selection_filter(self, idx: int) -> ArgumentsSelectFilter | None:
        command: bytearray = rcp_commands.get_selection_filter(idx)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_selection_filter(self, idx: int, target: ParamSelectTarget, action: ParamSelectAction, memory: ParamMemory,
                             pointer_bit: int, length_bit: int, mask: bytearray) -> OperationResult:
        command: bytearray = rcp_commands.set_selection_filter(idx, target, action, memory, pointer_bit, length_bit,
                                                               mask)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_selection_enables(self) -> List[bool]:
        command: bytearray = rcp_commands.get_selection_enables()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_selection_enables(self, mask: List[bool]) -> OperationResult:
        command: bytearray = rcp_commands.set_selection_enables(mask)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_region(self) -> Region:
        command: bytearray = rcp_commands.get_region()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_region(self, region: Region) -> OperationResult:
        command: bytearray = rcp_commands.set_region(region)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_tx_power(self) -> float:
        command: bytearray = rcp_commands.get_tx_power()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_tx_power(self, dbm: float) -> OperationResult:
        command: bytearray = rcp_commands.set_tx_power(dbm)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_fh_lbt_parameters(self) -> ArgumentsFhLbtParameters:
        command: bytearray = rcp_commands.get_fh_lbt_parameters()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_fh_lbt_parameters(self, dwell_time: int, idle_time: int, sense_time: int, lbt_rf_level: float,
                              fh_lbt_mode: ParamFhLbtMode) -> OperationResult:
        command: bytearray = rcp_commands.set_fh_lbt_parameters(dwell_time, idle_time, sense_time, lbt_rf_level,
                                                                fh_lbt_mode)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def get_rssi(self) -> float:
        command: bytearray = rcp_commands.get_rssi()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def set_cw(self, enable: bool) -> OperationResult:
        command: bytearray = rcp_commands.set_cw(enable)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def start_auto_read2(self, tag_type: TagType = TagType.TYPE_C, max_n_tags: int = 0, max_time_secs: int = 0,
                         repeat_cycle: int = 0) -> OperationResult:
        command: bytearray = rcp_commands.start_auto_read2(tag_type, max_n_tags, max_time_secs, repeat_cycle)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def stop_auto_read2(self) -> OperationResult:
        command: bytearray = rcp_commands.stop_auto_read2()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def start_auto_read_tid(self, max_n_tags: int = 0, max_time_secs: int = 0,
                            repeat_cycle: int = 0) -> OperationResult:
        command: bytearray = rcp_commands.start_auto_read_tid(max_n_tags, max_time_secs, repeat_cycle)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def stop_auto_read_tid(self) -> OperationResult:
        command: bytearray = rcp_commands.stop_auto_read_tid()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def start_auto_read_rssi(self, tag_type: TagType = TagType.TYPE_C, max_n_tags: int = 0, max_time_secs=0,
                             repeat_cycle: int = 0) -> OperationResult:
        command: bytearray = rcp_commands.start_auto_read_rssi(tag_type, max_n_tags, max_time_secs, repeat_cycle)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def stop_auto_read_rssi(self) -> OperationResult:
        command: bytearray = rcp_commands.stop_auto_read_rssi()
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)

    def read(self, epc, target_memory: ParamMemory, word_pointer: int, word_count: int = 1,
             access_password=bytearray([0, 0, 0, 0])) -> bytes | None:
        command: bytearray = rcp_commands.read(epc, target_memory, word_pointer, word_count, access_password)
        resp = self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)
        if type(resp) is ErrorMessage:
            return None
        return resp

    def write(self, epc, target_memory: ParamMemory, word_pointer: int, data: bytearray | str | int | List[int],
              access_password=bytearray([0, 0, 0, 0])) -> OperationResult:
        command: bytearray = rcp_commands.write(epc, target_memory, word_pointer, data, access_password)
        return self._txrx_cmd(command=command, name=inspect.currentframe().f_code.co_name)
