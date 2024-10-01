import time
from typing import List

from tests import reader

epc_list: List[str] | None = None


def autoread2_notification_callback(epc):
    global epc_list
    epc_list.append(epc)


def test_autoread2():
    global epc_list
    epc_list = []
    reader.set_notification_callback(autoread2_notification_callback)
    reader.start_auto_read2()
    time.sleep(1)
    reader.stop_auto_read2()
    assert len(epc_list) > 0
