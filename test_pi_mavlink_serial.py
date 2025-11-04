#!/usr/bin/env python3
"""Analyze MAVLink messages from Pixhawk serial connection"""
import sys

sys.path.insert(0, "/home/pi")

try:
    from pymavlink import mavutil
    import time
except ImportError as e:
    print(f"[❌] Import error: {e}")
    sys.exit(1)

print("[INFO] Connecting to /dev/ttyAMA0 @ 57600...")
try:
    mav = mavutil.mavlink_connection("/dev/ttyAMA0", baud=57600, timeout=2)
except Exception as e:
    print(f"[❌] Connection failed: {e}")
    sys.exit(1)

print("[INFO] Waiting for heartbeat...")
msg = mav.wait_heartbeat(timeout=5)

if msg:
    print(f"[✅] Heartbeat received!")
    print(f"    System ID: {msg.get_srcSystem()}")
    print(f"    Component ID: {msg.get_srcComponent()}")
    print(f"    System type: {msg.type}")
    print(f"    Base mode: {msg.base_mode}")
    print(f"    Custom mode: {msg.custom_mode}")

    # Request AUTOPILOT_VERSION
    print("\n[INFO] Requesting AUTOPILOT_VERSION...")
    mav.mav.command_long_send(
        mav.target_system,
        mav.target_component,
        mavutil.mavlink.MAV_CMD_REQUEST_MESSAGE,
        0,
        mavutil.mavlink.MAVLINK_MSG_ID_AUTOPILOT_VERSION,
        0,
        0,
        0,
        0,
        0,
        0,
    )

    # Try to receive version message
    try:
        version_msg = mav.recv_match(type="AUTOPILOT_VERSION", timeout=2)
        if version_msg:
            print(f"[✅] AUTOPILOT_VERSION received!")
            print(f"    Firmware: {version_msg.flight_sw_version:08x}")
        else:
            print("[⚠️] No AUTOPILOT_VERSION response")
    except Exception as e:
        print(f"[⚠️] Error: {e}")

    # Monitor other messages
    print("\n[INFO] Monitoring messages (3 seconds)...")
    start = time.time()
    while time.time() - start < 3:
        msg = mav.recv_match(timeout=0.5)
        if msg:
            print(f"    MSG: {msg.get_type()} (from SysID={msg.get_srcSystem()})")
else:
    print("[❌] No heartbeat received")

mav.close()
