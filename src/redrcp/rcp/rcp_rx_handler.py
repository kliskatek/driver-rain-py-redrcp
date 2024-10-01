import logging
import math
import time
from queue import Queue
from struct import unpack

from .error_messages import ErrorMessage
from ..rcp.enums import MessageConstants, MessageType, MessageCode, Region, ReaderInfoType, \
    ParamModulation, ParamDR, ParamSel, ParamSession, ParamTarget, ParamFhLbtMode, ParamSelectTarget, ParamSelectAction, \
    ParamMemory, ErrorCode, OperationResult
from ..rcp.message_arguments import ArgumentsReaderInformationDetail, ArgumentsCurrentRfChannel, \
    ArgumentsFrequencyHoppingTable, ArgumentsAntiCollisionMode, ArgumentsModulationMode, \
    ArgumentsFhLbtParameters, NotificationTpeCuiii, NotificationTpeCuiiiRssi, ArgumentsQueryParameters, \
    NotificationTpeCuiiiTid, ArgumentsSelectFilter

logger = logging.getLogger(__name__)


class RcpRxHandler:

    def __init__(self):
        self.buffer = bytearray()
        self.response_queue = Queue()
        self.notification_callback = None

    def set_notification_callback(self, notification_callback):
        self.notification_callback = notification_callback

    def append_data(self, data: bytearray | bytes | None):
        if data is not None:
            self.buffer += data
            self._try_parse_data()

    def _try_parse_data(self):
        try:
            # Discard data until PREAMBLE
            start = self.buffer.find(bytearray([MessageConstants.PREAMBLE.value]))
            if start > 0:
                logger.warning('Syching PREAMBLE.')
                self.buffer = self.buffer[start:]

            while len(self.buffer) > 4:
                payload_len = (self.buffer[3] << 8) + self.buffer[4]

                if len(self.buffer) > 7 + payload_len:
                    # Check END_MARK
                    if self.buffer[5 + payload_len] != MessageConstants.ENDMARK.value:
                        logger.warning('Incorrect END MARK. Discarding data.')
                        del self.buffer[0:7 + payload_len]

                    # Check CRC (Not implemented)

                    # Extract data
                    message_type = MessageType(self.buffer[1])
                    message_code = MessageCode(self.buffer[2])
                    payload = self.buffer[5:5 + payload_len]

                    # Process message
                    self._process_message(message_type, message_code, payload)

                    # Remove processed data
                    del self.buffer[0:8 + payload_len]
                else:
                    # logger.warning('Missing payload data.')
                    break
        except Exception as e:
            logger.error(e)

    def _process_message(self, message_type: MessageType, message_code: MessageCode, payload: bytearray):
        if MessageType(message_type) == MessageType.RESPONSE:
            if MessageCode(message_code) == MessageCode.ERROR:
                self._process_error(payload)
            if MessageCode(message_code) == MessageCode.GET_REGISTRY_ITEM:
                self._process_get_registry_item(payload)
            if MessageCode(message_code) == MessageCode.GET_READER_INFORMATION:
                self._process_get_reader_info(payload)
            if MessageCode(message_code) == MessageCode.GET_CURRENT_RF_CHANNEL:
                self._process_get_current_rf_channel(payload)
            if MessageCode(message_code) == MessageCode.GET_FREQUENCY_HOPPING_TABLE:
                self._process_get_frequency_hopping_table(payload)
            if MessageCode(message_code) == MessageCode.GET_ANTI_COLLISION_MODE:
                self._process_get_anti_collision_mode(payload)
            if MessageCode(message_code) == MessageCode.GET_MODULATION:
                self._process_get_modulation_mode(payload)
            if MessageCode(message_code) == MessageCode.GET_TYPE_QUERY_RELATED_PARAMETERS:
                self._process_get_query_parameters(payload)
            if MessageCode(message_code) == MessageCode.GET_SELECTION_FILTER:
                self._process_get_selection_filter(payload)
            if MessageCode(message_code) == MessageCode.GET_SELECTION_ENABLES:
                self._process_get_selection_enables(payload)
            if MessageCode(message_code) == MessageCode.GET_REGION:
                self._process_get_region(payload)
            if MessageCode(message_code) == MessageCode.GET_TX_POWER:
                self._process_get_tx_power(payload)
            if MessageCode(message_code) == MessageCode.RCP_CMD_GET_TX_PWR_RAW:
                self._process_get_tx_power_raw(payload)
            if MessageCode(message_code) == MessageCode.GET_FH_LBT_PARAMETERS:
                self._process_get_fh_lbt_parameters(payload)
            if MessageCode(message_code) == MessageCode.GET_RSSI:
                self._process_get_rssi(payload)
            if MessageCode(message_code) == MessageCode.READ_TPE_C_TAG_DATA:
                self._process_read(payload)
            if MessageCode(message_code) in [
                                                MessageCode.RF_CW_SIGNAL_CONTROL,
                                                MessageCode.START_AUTO_READ2,
                                                MessageCode.STOP_AUTO_READ2,
                                                MessageCode.START_AUTO_READ_RSSI,
                                                MessageCode.STOP_AUTO_READ_RSSI,
                                                MessageCode.WRITE_TYPE_C_TAG_DATA,
                                                MessageCode.SET_SYSTEM_RESET,
                                                MessageCode.BLOCK_WRITE_TYPE_C_TAG_DATA,
                                                MessageCode.BLOCK_PERMALOCK_TYPE_C_TAG,
                                                MessageCode.LOCK_TYPE_C_TAG,
                                                MessageCode.KILL_RECOM_TYPE_C_TAG,
                                                MessageCode.SET_ANTI_COLLISION_MODE,
                                                MessageCode.SET_MODULATION,
                                                MessageCode.SET_TYPE_QUERY_RELATED_PARAMETERS,
                                                MessageCode.SET_SELECTION_FILTER,
                                                MessageCode.SET_SELECTION_ENABLES,
                                                MessageCode.SET_REGION,
                                                MessageCode.SET_TX_POWER,
                                                MessageCode.RCP_CMD_SET_TX_PWR_RAW,
                                                MessageCode.SET_FH_LBT_PARAMETERS,
                                            ]:
                self._process_success_or_error(payload)
        if MessageType(message_type) == MessageType.NOTIFICATION:
            if MessageCode(message_code) == MessageCode.READ_TPE_CUIII:
                self._process_read_tpe_cuiii(payload)
            if MessageCode(message_code) == MessageCode.READ_TPE_CUIII_RSSI:
                self._process_read_tpe_cuiii_rssi(payload)
            if MessageCode(message_code) == MessageCode.READ_TPE_CUIII_TID:
                self._process_read_tpe_cuiii_tid(payload)

    def reset_response_queue(self):
        self.response_queue = Queue()

    def get_response(self, timeout_s=3):
        start_timestamp = time.time()
        while self.response_queue.empty():
            time.sleep(.001)
            current_timestamp = time.time()
            if current_timestamp - start_timestamp > timeout_s:
                raise TimeoutError
        return self.response_queue.get()

    def _process_success_or_error(self, payload):
        self.response_queue.put(OperationResult(payload[0]))

    def _process_error(self, payload):
        try:
            command_code = MessageCode(payload[1])
            error_code = ErrorCode(payload[2])
            return_value = ErrorMessage(command_code, error_code)
            self.response_queue.put(return_value)
        except Exception as e:
            logger.warning("Exception while processing RedRcp error message: " + str(e))
            logger.warning("Returning default error signal")
            self.response_queue.put(OperationResult.ERROR)

    def _process_get_registry_item(self, payload):
        self.response_queue.put(payload)

    def _process_get_reader_info(self, payload):
        if payload[0] == ReaderInfoType.DETAIL.value:
            info = ArgumentsReaderInformationDetail()
            info.region = Region(payload[1])
            info.channel = payload[2]
            info.read_time = unpack('>H', payload[3:5])[0]
            info.idle_time = unpack('>H', payload[5:7])[0]
            info.cw_sense_time = unpack('>H', payload[7:9])[0]
            info.lbt_rf_level = unpack('>h', payload[9:11])[0] / 10
            info.current_tx_power = unpack('>H', payload[14:16])[0] / 10
            info.min_tx_power = unpack('>H', payload[16:18])[0] / 10
            info.max_tx_power = unpack('>H', payload[18:20])[0] / 10
            info.BLF = payload[21]
            info.modulation = ParamModulation(payload[22])
            info.DR = ParamDR(payload[23])
        else:
            # Response is string
            info = payload.decode(encoding='latin-1').strip('\x00')
        self.response_queue.put(info)

    def _process_get_current_rf_channel(self, payload):
        resp = ArgumentsCurrentRfChannel()
        resp.channel = payload[0]
        resp.offset = payload[1]
        self.response_queue.put(resp)

    def _process_get_frequency_hopping_table(self, payload):
        resp = ArgumentsFrequencyHoppingTable()
        resp.size = payload[0]
        resp.channels = []
        for i in range(resp.size):
            resp.channels.append(payload[i + 1])
        self.response_queue.put(resp)

    def _process_get_anti_collision_mode(self, payload):
        resp = ArgumentsAntiCollisionMode()
        resp.mode = payload[0]
        resp.initial_q = payload[1]
        resp.max_q = payload[2]
        resp.min_q = payload[3]
        self.response_queue.put(resp)

    def _process_get_modulation_mode(self, payload):
        resp = ArgumentsModulationMode()
        resp.BLF = unpack('>H', payload[0:2])[0]
        resp.modulation = ParamModulation(payload[2])
        resp.DR = ParamDR(payload[3])
        self.response_queue.put(resp)

    def _process_get_query_parameters(self, payload):
        query_parameters = ArgumentsQueryParameters()
        query_parameters.DR = ParamDR((payload[0] >> 7) & 0x01)
        query_parameters.modulation = ParamModulation((payload[0] >> 5) & 0x03)
        query_parameters.pilot_tone = (payload[0] >> 4) & 0x01
        query_parameters.sel = ParamSel((payload[0] >> 2) & 0x03)
        query_parameters.session = ParamSession(payload[0] & 0x03)
        query_parameters.target = ParamTarget((payload[1] >> 7) & 0x01)
        query_parameters.target_toggle = payload[1] & 0x01
        query_parameters.q = (payload[1] >> 3) & 0x0F
        self.response_queue.put(query_parameters)

    def _process_get_selection_filter(self, payload):
        select_filter = ArgumentsSelectFilter()
        select_filter.index = payload[0]
        select_filter.target = ParamSelectTarget(payload[1])
        select_filter.action = ParamSelectAction(payload[2])
        select_filter.memory = ParamMemory(payload[3])
        select_filter.pointer = unpack('>H', payload[4:6])[0]
        select_filter.length = payload[6]
        select_filter.mask = payload[7:]
        self.response_queue.put(select_filter)

    def _process_get_selection_enables(self, payload):
        mask = payload[0]
        enables = []
        for i in range(8):
            enables.append(bool(mask & (1 << i)))

        self.response_queue.put(enables)

    def _process_get_region(self, payload):
        region = Region(payload[0])
        self.response_queue.put(region)

    def _process_get_tx_power(self, payload):
        tx_power = unpack('>H', payload[0:2])[0] / 10
        self.response_queue.put(tx_power)

    def _process_get_tx_power_raw(self, payload):
        mode = payload[0]
        gain = unpack('>H', payload[1:3])[0]
        self.response_queue.put([mode, gain])

    def _process_get_fh_lbt_parameters(self, payload):
        resp = ArgumentsFhLbtParameters()
        resp.dwell_time = unpack('>H', payload[0:2])[0]
        resp.idle_time = unpack('>H', payload[2:4])[0]
        resp.sense_time = unpack('>H', payload[4:6])[0]
        resp.lbt_rf_level = unpack('>h', payload[6:8])[0] / 10
        resp.fh_lbt_mode = ParamFhLbtMode(unpack('>H', payload[8:10])[0])
        self.response_queue.put(resp)

    def _process_get_rssi(self, payload):
        rssi = -unpack('>H', payload[0:2])[0] / 10
        self.response_queue.put(rssi)

    def _process_read(self, payload):
        self.response_queue.put(payload)

    def _process_read_tpe_cuiii(self, payload):
        tag = NotificationTpeCuiii()
        tag.pc = payload[0:2]
        tag.epc = payload[2:]
        epc = payload[2:]
        if self.notification_callback is not None:
            self.notification_callback(tag)

    def _process_read_tpe_cuiii_rssi(self, payload):
        tag = NotificationTpeCuiiiRssi()
        tag.pc = payload[0:2]
        tag.epc = payload[2:-4]
        rssi_i = payload[-4]
        rssi_q = payload[-3]
        gain_i = payload[-2]
        gain_q = payload[-1]
        try:
            if rssi_i > 0:
                rfin_i = (20 * math.log10(rssi_i) - gain_i - 33 - 30)
                rfin_i = math.pow(10, (rfin_i / 20))
            else:
                rfin_i = 0
            if rssi_q > 0:
                rfin_q = (20 * math.log10(rssi_q) - gain_q - 33 - 30)
                rfin_q = math.pow(10, (rfin_q / 20))
            else:
                rfin_q = 0
            tag.rssi = round(20 * math.log10(math.sqrt(math.pow(rfin_i, 2) + math.pow(rfin_q, 2))), 1)
        except Exception as e:
            tag.rssi = -1
        if self.notification_callback is not None:
            self.notification_callback(tag)

    def _process_read_tpe_cuiii_tid(self, payload):
        tag = NotificationTpeCuiiiTid()
        tag.pc = payload[0:2]
        epc_length = (tag.pc[0] & 0b11111000) >> 3
        tag.epc = payload[2:2 + epc_length * 2]
        tag.tid = payload[2 + epc_length * 2:]
        if self.notification_callback is not None:
            self.notification_callback(tag)
