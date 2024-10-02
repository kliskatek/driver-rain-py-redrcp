import logging
import time
from binascii import hexlify

from redrcp import RedRcp, ParamMemory, NotificationTpeCuiii

logging.basicConfig(level=logging.DEBUG)
reader = RedRcp()
reader.connect(connection_string='COM3')

manufacturer = reader.get_info_manufacturer()
model = reader.get_info_model()
details = reader.get_info_detail()

reader.set_tx_power(27)

some_tag: NotificationTpeCuiii | None = None


def autoread_notification_callback(tag: NotificationTpeCuiii):
    global some_tag
    logging.info(tag)
    if some_tag is None:
        some_tag = tag


reader.set_notification_callback(autoread_notification_callback)
reader.start_auto_read2()
time.sleep(.1)
reader.stop_auto_read2()
# reader.start_auto_read_tid()
# time.sleep(.1)
# reader.stop_auto_read_tid()
# reader.start_auto_read_rssi()
# time.sleep(.1)
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
