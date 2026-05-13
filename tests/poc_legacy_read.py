"""
PoC of the LEGACY-mode loop the SDK wrapper runs on the RED4S.

Rotating ops: every OP_PERIOD_S we run one operation from a list
  [inventory, read sensor_1, read sensor_2, …]
The inventory slot refreshes the EPC list (tags can come and go);
the read slots stream the user-memory blob of each sensor tag.

CW does NOT need to be re-set between Reads on the RED4S — it stays
on for the whole burst (verified empirically). The reader manages
CW itself when transitioning between Read/auto_read/idle.

Useful as a smoke-check / spectrum-analyser companion when tuning
the duty cycle.
"""

import logging
import time

from redrcp import RedRcp, ParamMemory


PORT = "COM4"
TX_POWER_DBM = 27
WORD_PTR = 0x100
WORD_COUNT = 6
INVENTORY_WINDOW_S = 0.3    # how long the inventory burst holds the air
OP_PERIOD_S = 0.10          # min start-to-start spacing per operation
RUN_S = 10

# Only Reads on tags whose EPC matches these PEN prefixes; others are
# reported once and ignored to avoid burning the driver's 3 s timeout.
LEGACY_PEN  = bytes.fromhex('000000F1D3')
FARSENS_PEN = bytes.fromhex('000000A93C')

logging.basicConfig(level=logging.WARNING)


def is_sensor_epc(epc_hex: str) -> bool:
    try:
        b = bytes.fromhex(epc_hex)
    except ValueError:
        return False
    return b.startswith(LEGACY_PEN) or b.startswith(FARSENS_PEN)


def main():
    reader = RedRcp()
    if not reader.connect(PORT):
        print(f"Could not connect to {PORT}")
        return
    seen_epcs: set[str] = set()
    reader.set_notification_callback(
        lambda notif: seen_epcs.add(bytes(notif.epc).hex().upper())
    )
    reader.set_tx_power(TX_POWER_DBM)

    sensor_epcs: list[str] = []
    seen_passthrough: set[str] = set()
    counts: dict[str, list] = {}

    def record(epc: str, blob):
        entry = counts.setdefault(epc, [0, None])
        entry[0] += 1
        if blob and entry[1] is None:
            entry[1] = blob

    def do_inventory():
        seen_epcs.clear()
        reader.start_auto_read2()
        time.sleep(INVENTORY_WINDOW_S)
        reader.stop_auto_read2()
        new_sensor = [e for e in seen_epcs if is_sensor_epc(e)]
        sensor_epcs[:] = [e for e in sensor_epcs if e in new_sensor] + \
                         [e for e in new_sensor if e not in sensor_epcs]
        for epc in seen_epcs - set(sensor_epcs):
            if epc not in seen_passthrough:
                seen_passthrough.add(epc)
                record(epc, None)
                print(f"[passthrough] {epc}")

    def do_read(epc: str):
        try:
            data = reader.read(epc, ParamMemory.USER, WORD_PTR, WORD_COUNT)
        except Exception as e:
            print(f"read({epc}) error: {e}")
            data = None
        blob = bytes(data).hex().upper() if data else None
        record(epc, blob)

    deadline = time.monotonic() + RUN_S
    op_idx = 0
    try:
        while time.monotonic() < deadline:
            op_start = time.monotonic()
            ops_len = 1 + len(sensor_epcs)
            op = op_idx % ops_len
            op_idx += 1
            if op == 0:
                do_inventory()
            else:
                do_read(sensor_epcs[op - 1])
            elapsed = time.monotonic() - op_start
            remaining = OP_PERIOD_S - elapsed
            if remaining > 0:
                time.sleep(remaining)
    finally:
        reader.set_cw(False)
        reader.disconnect()

    print("\nSummary:")
    for epc, (cnt, first) in sorted(counts.items(), key=lambda kv: -kv[1][0]):
        rate = cnt / RUN_S
        print(f"  {cnt:4d}x ({rate:.1f}/s)  EPC={epc}  first_data={first or '<none>'}")


if __name__ == "__main__":
    main()
