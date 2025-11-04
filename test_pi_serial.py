#!/usr/bin/env python3
"""Test serial connection to Pixhawk on Raspberry Pi"""
import sys

sys.path.insert(0, "/home/pi")

try:
    import serial

    print("[✅] PySerial imported")
except ImportError:
    print("[❌] PySerial not installed")
    sys.exit(1)

try:
    print("\n[INFO] Attempting to open /dev/ttyAMA0 @ 57600 baud...")
    port = serial.Serial("/dev/ttyAMA0", 57600, timeout=1)
    print("[✅] Serial port opened successfully")

    # Try to read data
    import time

    time.sleep(0.5)
    data = port.read(100)
    if data:
        print(f"[✅] Received data: {len(data)} bytes")
        print(f"    Raw: {data[:20]}...")  # Show first 20 bytes
    else:
        print("[⚠️] No data received (Pixhawk may not be sending)")

    port.close()
    print("[✅] Serial port closed")

except Exception as e:
    print(f"[❌] Error: {e}")
    sys.exit(1)
