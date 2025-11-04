#!/usr/bin/env python3
"""
Check Pixhawk system status and capabilities.
Verify if Pixhawk is real and what firmware it's running.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.connections.mavlinkConnection import PixhawkConnection


def check_pixhawk_system():
    """Check Pixhawk system info and capabilities."""

    print("=" * 70)
    print("PIXHAWK SYSTEM CHECK")
    print("=" * 70)

    # Connect
    print("\n[1] Connecting to Pixhawk...")
    pixhawk = PixhawkConnection(link="tcp:raspberrypi.local:7000", auto_detect=False)

    if not pixhawk.connect():
        print("[❌] Cannot connect to Pixhawk")
        return False

    print("[✅] Connected")

    # Try to get AUTOPILOT_VERSION
    print("\n[2] Requesting system version...")
    try:
        pixhawk.vehicle.mav.command_long_send(
            pixhawk.vehicle.target_system,
            pixhawk.vehicle.target_component,
            178,  # MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES
            0,
            1,  # 1 = request capabilities
            0,
            0,
            0,
            0,
            0,
            0,
        )

        # Wait for AUTOPILOT_VERSION message
        for i in range(20):
            msg = pixhawk.vehicle.recv_match(
                type="AUTOPILOT_VERSION", blocking=False, timeout=0
            )
            if msg:
                print(f"[✅] Got AUTOPILOT_VERSION")
                print(f"    Flight SW Version: {msg.flight_sw_version}")
                print(f"    Board ID: {msg.board_version}")
                break
            time.sleep(0.1)
        else:
            print(f"[⚠️] No AUTOPILOT_VERSION received")
    except Exception as e:
        print(f"[⚠️] Could not request version: {e}")

    # Check SYSTEM_TIME
    print("\n[3] Checking system time...")
    try:
        pixhawk.vehicle.mav.command_long_send(
            pixhawk.vehicle.target_system,
            pixhawk.vehicle.target_component,
            156,  # MAV_CMD_DO_SET_HOME
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        )

        msg = pixhawk.vehicle.recv_match(type="SYSTEM_TIME", blocking=False, timeout=2)
        if msg:
            print(f"[✅] System time: {msg.time_unix_usec}")
        else:
            print(f"[⚠️] No SYSTEM_TIME response")
    except Exception as e:
        print(f"[⚠️] Error: {e}")

    # Check if we can receive STATUS_TEXT (debug messages)
    print("\n[4] Monitoring status messages (5 seconds)...")
    start = time.time()
    status_count = 0

    while time.time() - start < 5:
        msg = pixhawk.vehicle.recv_match(type="STATUSTEXT", blocking=False, timeout=0)
        if msg:
            status_count += 1
            severity = (
                [
                    "EMERGENCY",
                    "ALERT",
                    "CRITICAL",
                    "ERROR",
                    "WARNING",
                    "NOTICE",
                    "INFO",
                    "DEBUG",
                ][msg.severity]
                if hasattr(msg, "severity")
                else "?"
            )
            print(f"    [{severity}] {msg.text.decode('utf-8', errors='ignore')}")

        time.sleep(0.1)

    if status_count == 0:
        print(f"    ⚠️ No status messages received")
    else:
        print(f"    ✅ Got {status_count} status messages")

    # Check heartbeat info
    print("\n[5] Heartbeat information...")
    print(f"    Target System: {pixhawk.vehicle.target_system}")
    print(f"    Target Component: {pixhawk.vehicle.target_component}")
    print(f"    System Type: {pixhawk.vehicle.target_system & 0xFF}")

    pixhawk.close()

    print("\n" + "=" * 70)
    print("SYSTEM CHECK COMPLETE")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        check_pixhawk_system()
    except Exception as e:
        print(f"\n[❌] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
