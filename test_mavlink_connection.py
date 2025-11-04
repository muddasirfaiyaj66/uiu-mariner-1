#!/usr/bin/env python3
"""
Test MAVLink connection to verify the issue
"""
from pymavlink import mavutil
import sys


def test_connection(link):
    """Test a MAVLink connection string"""
    print(f"\n{'='*60}")
    print(f"Testing connection: {link}")
    print(f"{'='*60}")

    try:
        print("[1] Creating connection...")
        vehicle = mavutil.mavlink_connection(link)

        print("[2] Waiting for heartbeat (10 second timeout)...")
        vehicle.wait_heartbeat(timeout=10)

        print(f"[✅] SUCCESS! Heartbeat received")
        print(f"    System ID: {vehicle.target_system}")
        print(f"    Component ID: {vehicle.target_component}")

        vehicle.close()
        return True

    except Exception as e:
        print(f"[❌] FAILED: {type(e).__name__}: {e}")
        return False


# Test different connection formats
test_cases = [
    "tcp:raspberrypi.local:7000",
    "tcp:192.168.0.102:7000",
    "tcpin:raspberrypi.local:7000",
    "tcpin:192.168.0.102:7000",
]

print("\n" + "=" * 60)
print("MAVLink Connection Test Suite")
print("=" * 60)

results = {}
for link in test_cases:
    results[link] = test_connection(link)

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
for link, success in results.items():
    status = "✅ SUCCESS" if success else "❌ FAILED"
    print(f"{status}: {link}")

print("\n")
