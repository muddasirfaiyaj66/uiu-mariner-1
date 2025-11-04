#!/usr/bin/env python3
from pymavlink import mavutil
import time

print("Testing direct Pixhawk connection on /dev/ttyACM1...")
print("=" * 60)

try:
    m = mavutil.mavlink_connection("/dev/ttyACM1", baud=115200)
    print("Waiting for heartbeat (10 second timeout)...")

    msg = m.wait_heartbeat(timeout=10)

    if msg:
        print("✅ HEARTBEAT RECEIVED!")
        print(f"   Type: {msg.type}")
        print(f"   Autopilot: {msg.autopilot}")
        print(f"   System ID: {msg.get_srcSystem()}")
        print(f"   Component ID: {msg.get_srcComponent()}")

        # Try to get a few more heartbeats
        print("\nMonitoring for 5 more heartbeats...")
        for i in range(5):
            msg = m.recv_match(type="HEARTBEAT", blocking=True, timeout=2)
            if msg:
                print(f"  {i+1}. Heartbeat OK")
            else:
                print(f"  {i+1}. NO HEARTBEAT!")
                break

        print("\n✅ Connection is stable")
    else:
        print("❌ NO HEARTBEAT RECEIVED")
        print("Check:")
        print("  - Pixhawk power")
        print("  - USB cable")
        print("  - Pixhawk boot status (LEDs)")

except Exception as e:
    print(f"❌ ERROR: {e}")
