"""
PoC: Phychips RED4S — read legacy / Farsens user-memory by alternating
short inventory windows with explicit Read() calls under CW.

The RED4S has no embedded-read primitive (unlike the R700 / Speedway),
so the loop is:

  1. start_auto_read2()           — quick inventory window
  2. wait INVENTORY_WINDOW_MS     — accumulate seen EPCs in callback
  3. stop_auto_read2()
  4. set_cw(True)                 — keep tags powered between reads
  5. for each EPC: read(USER, 0x100, WORD_COUNT)
  6. set_cw(False)
  7. repeat
"""

import logging
import time

from redrcp import (
    RedRcp,
    AntiCollisionMode,
    ParamDR, ParamFhLbtMode, ParamMemory, ParamModulation,
    ParamSel, ParamSession, ParamTarget,
)


PORT = "COM4"
WORD_PTR = 0x100
WORD_COUNT = 6
INVENTORY_WINDOW_MS = 500
LOOP_S = 8
TX_POWER_DBM = 25.0

logging.basicConfig(level=logging.WARNING)


def main():
    reader = RedRcp()
    if not reader.connect(PORT):
        print(f"Could not connect to {PORT}")
        return

    seen_epcs = set()

    def on_notification(notif):
        # bytearray is not hashable; store as hex string
        try:
            seen_epcs.add(bytes(notif.epc).hex().upper())
        except Exception as e:
            print(f"callback err: {e}")

    reader.set_notification_callback(on_notification)
    reader.set_tx_power(TX_POWER_DBM)
    # NOTE: set_anti_collision_mode / set_query_parameters / get_info_detail
    # break the next auto_read2 cycle on this firmware (RED4S_v2.2.1_K).
    # Whatever the reader has in NVM works — leave it alone.

    # Baseline test: just inventory for the full window, see if the reader
    # reports any tags at all. If this is empty too, the problem is config
    # (not the loop / timing).
    print(f"\nBaseline inventory (no loop) for 3 s on {PORT}…")
    seen_epcs.clear()
    reader.start_auto_read2()
    time.sleep(3.0)
    reader.stop_auto_read2()
    print(f"  baseline saw {len(seen_epcs)} unique EPC(s): {list(seen_epcs)[:5]}")

    print(f"\nReading on {PORT} for {LOOP_S} s. Bring legacy/Farsens tags close…")
    summary = {}  # epc -> [(count, first_user_mem_hex)]
    deadline = time.monotonic() + LOOP_S
    cycle = 0
    try:
        while time.monotonic() < deadline:
            cycle += 1
            seen_epcs.clear()
            reader.start_auto_read2()
            time.sleep(INVENTORY_WINDOW_MS / 1000.0)
            reader.stop_auto_read2()
            if not seen_epcs:
                continue
            reader.set_cw(True)
            try:
                for epc in list(seen_epcs):
                    data = reader.read(epc, ParamMemory.USER, WORD_PTR, WORD_COUNT)
                    blob = bytes(data).hex().upper() if data else None
                    entry = summary.setdefault(epc, [0, None])
                    entry[0] += 1
                    if blob and entry[1] is None:
                        entry[1] = blob
                    print(f"[cycle {cycle}] EPC={epc} user_mem={blob or '<read failed>'}")
            finally:
                reader.set_cw(False)
    finally:
        reader.disconnect()

    print("\nSummary:")
    for epc, (cnt, first_blob) in summary.items():
        print(f"  {cnt:3d}x  EPC={epc}  first_data={first_blob or '<none>'}")


if __name__ == "__main__":
    main()
