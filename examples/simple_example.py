import logging
import time
from binascii import hexlify


# To use from source
from src.redrcp import RedRcp, ParamMemory, NotificationTpeCuiii

# To use from installed package
#from redrcp import RedRcp, ParamMemory, NotificationTpeCuiii


logging.basicConfig(level=logging.DEBUG)

reader = RedRcp()

reader.connect(connection_string='COM3')  # windows
#reader.connect(connection_string='/dev/ttyUSB0')  # linux
#reader.connect(connection_string='/dev/tty.usbserial-001')  # macos

manufacturer = reader.get_info_manufacturer()
model = reader.get_info_model()
fw_version = reader.get_info_fw_version()
details = reader.get_info_detail()

reader.set_tx_power(27)

some_tag: NotificationTpeCuiii | None = None


def autoread_notification_callback(tag: NotificationTpeCuiii):
    global some_tag
    logging.info(tag)
    if some_tag is None:
        some_tag = tag


reader.set_notification_callback(autoread_notification_callback)

# Start inventory
reader.start_auto_read2()
# reader.start_auto_read_tid()
# reader.start_auto_read_rssi()

# Do other stuff
time.sleep(.5)

# Start inventory
reader.stop_auto_read2()
# reader.stop_auto_read_tid()
# reader.stop_auto_read_rssi()

res = reader.write(epc=some_tag.epc, target_memory=ParamMemory.USER, word_pointer=0, data='1234')
logging.info(res)
res = reader.read(epc=some_tag.epc, target_memory=ParamMemory.USER, word_pointer=0, word_count=1)
if res is not None:
    logging.info(hexlify(res))
res = reader.write(epc=some_tag.epc, target_memory=ParamMemory.USER, word_pointer=0, data='5678')
logging.info(res)
res = reader.read(epc=some_tag.epc, target_memory=ParamMemory.USER, word_pointer=0, word_count=1)
if res is not None:
    logging.info(hexlify(res))
