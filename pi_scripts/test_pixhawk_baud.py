#!/usr/bin/env python3
"""Quick Pixhawk test at different baud rates"""
from pymavlink import mavutil
import sys

bauds = [57600, 115200, 921600, 38400]
port = "/dev/ttyAMA0"

for baud in bauds:
    print(f"Testing {port} @ {baud} baud...")
    try:
        conn = mavutil.mavlink_connection(port, baud=baud)
        msg = conn.wait_heartbeat(timeout=5)
        if msg:
            print(f"✅ SUCCESS at {baud} baud!")
            print(f"   Type: {msg.type}, Autopilot: {msg.autopilot}, System: {msg.get_srcSystem()}")
            conn.close()
            sys.exit(0)
        else:
            print(f"   No heartbeat at {baud}")
        conn.close()
    except Exception as e:
        print(f"   Error: {e}")

print("\n❌ No connection at any baud rate")
print("Check: Pixhawk power, wiring (TX→RX, RX→TX, GND)")
