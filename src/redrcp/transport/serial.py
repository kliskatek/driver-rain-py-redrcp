import logging

import serial
from serial.serialutil import SerialException

logger = logging.getLogger(__name__)


class SerialPort:
    def __init__(self):
        self.serial = serial.Serial(
            baudrate=115200,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS
        )

    def connect(self, port) -> bool:
        if self.serial.isOpen():
            logger.info('RedRcp.Transport.SerialPort already connected.')
            return True
        try:
            self.serial.port = port
            self.serial.open()
            logger.info('RedRcp.Transport.SerialPort successfully connected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def is_connected(self) -> bool:
        return self.serial.isOpen()

    def disconnect(self) -> bool:
        if not self.is_connected():
            logger.info('RedRcp.Transport.SerialPort already disconnected.')
            return True
        try:
            self.serial.close()
            logger.info('RedRcp.Transport.SerialPort successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def write(self, data: bytes):
        self.serial.write(data)

    def read(self) -> bytes | None:
        try:
            data = self.serial.read_all()
            if len(data) > 0:
                logger.debug('RX << ' + str(data.hex(sep=' ').upper()))
                return data
        except SerialException:
            logger.info('RedRcp.Transport.SerialPort disconnected.')
            self.serial.close()
