#!/usr/bin/env python3
"""
Simple thruster test - RC override commands
"""

from pymavlink import mavutil
import time

print("=" * 60)
print("SIMPLE THRUSTER TEST")
print("=" * 60)

print("\n[1] Connecting to Pixhawk...")
try:
    vehicle = mavutil.mavlink_connection("tcp:192.168.0.106:7000", timeout=5)
    hb = vehicle.wait_heartbeat(timeout=10)
    if hb:
        print("[OK] Connected!")
    else:
        print("[ERROR] No heartbeat")
        exit(1)
except Exception as e:
    print(f"[ERROR] {e}")
    exit(1)

print("\n[2] Sending neutral RC (1500 PWM on all channels)...")
for i in range(5):
    neutral = [1500] * 8
    vehicle.mav.rc_channels_override_send(vehicle.target_system, vehicle.target_component, *neutral)
    print(f"    Sent {i+1}/5")
    time.sleep(0.2)

print("\n[3] Testing thruster ramp-up (channel 3)...")
for pwm in [1500, 1550, 1600, 1650, 1700, 1800, 2000]:
    channels = [1500, 1500, pwm, 1500, 1500, 1500, 1500, 1500]
    vehicle.mav.rc_channels_override_send(vehicle.target_system, vehicle.target_component, *channels)
    print(f"    Channel 3: {pwm} PWM")
    time.sleep(0.2)

print("\n[4] Return to neutral...")
neutral = [1500] * 8
vehicle.mav.rc_channels_override_send(vehicle.target_system, vehicle.target_component, *neutral)
print("    Done")

print("\n" + "=" * 60)
print("TEST COMPLETE - Thrusters should have responded!")
print("=" * 60)
