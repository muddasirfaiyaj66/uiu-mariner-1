#!/usr/bin/env python3
from pymavlink import mavutil
import time

print("Connecting...")
vehicle = mavutil.mavlink_connection('/dev/ttyAMA0', baud=57600)
print("Waiting for heartbeat...")
hb = vehicle.wait_heartbeat(timeout=5)
print(f"Heartbeat: {hb}")

# Read the first heartbeat message that was already received
print(f"\nMessage object attributes:")
print(f"  Type: {type(hb)}")

# Try to get the bytes
print(f"\nTrying different methods to encode:")

# Method 1: Try msg.get_memoryview()
if hasattr(hb, 'get_memoryview'):
    try:
        mv = hb.get_memoryview()
        print(f"  get_memoryview() worked: {len(mv)} bytes")
    except Exception as e:
        print(f"  get_memoryview() failed: {e}")

# Method 2: Try msg._msgbuf
if hasattr(hb, '_msgbuf'):
    try:
        buf = hb._msgbuf
        print(f"  _msgbuf: {buf}")
    except Exception as e:
        print(f"  _msgbuf failed: {e}")

# Method 3: Check the message class
print(f"\nMessage class methods:")
methods = [x for x in dir(hb) if 'buf' in x.lower() or 'serial' in x.lower() or 'pack' in x.lower()]
print(f"  {methods}")

# Try to see raw data attributes
print(f"\nAll non-private attributes:")
attrs = [x for x in dir(hb) if not x.startswith('_')][:20]
for attr in attrs:
    try:
        val = getattr(hb, attr)
        if not callable(val):
            print(f"  {attr}: {val}")
    except:
        pass
