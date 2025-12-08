#!/usr/bin/env python3
"""
Direct Thruster Test - Tests RC_CHANNELS_OVERRIDE commands to Pixhawk
This bypasses the UI and tests direct MAVLink communication.
"""

import time
from pymavlink import mavutil

print("=" * 70)
print("DIRECT THRUSTER TEST")
print("=" * 70)
print()

# Connect to Pixhawk via MAVProxy/TCP relay on Pi
CONNECTION_STRING = "tcp:192.168.0.106:7000"
print(f"[STEP 1] Connecting to Pixhawk via {CONNECTION_STRING}...")

try:
    vehicle = mavutil.mavlink_connection(CONNECTION_STRING, timeout=5)
    print("[WAIT] Waiting for heartbeat (up to 10 seconds)...")
    
    heartbeat = vehicle.wait_heartbeat(timeout=10)
    if heartbeat is None:
        print("[ERROR] No heartbeat received - Pixhawk not responding!")
        print("[TIP] Make sure MAVProxy is running on Pi: screen -r mavproxy")
        exit(1)
    
    print("[OK] ✅ Heartbeat received!")
    print(f"    System ID: {vehicle.target_system}")
    print(f"    Component ID: {vehicle.target_component}")
    print()
    
except Exception as e:
    print(f"[ERROR] Connection failed: {e}")
    exit(1)

# Get current vehicle state
print("[STEP 2] Checking vehicle state...")
try:
    print(f"    Flight Mode: {vehicle.flightmode}")
    print(f"    Armed: {vehicle.armed}")
    print()
except Exception as e:
    print(f"[WARNING] Could not read vehicle state: {e}")
    print()

# Test 1: Send neutral RC commands
print("[STEP 3] Sending NEUTRAL RC commands to all thrusters...")
print("         (1500 PWM = no thrust)")
try:
    neutral_channels = [1500] * 8
    vehicle.mav.rc_channels_override_send(
        vehicle.target_system, 
        vehicle.target_component,
        *neutral_channels
    )
    print("[OK] ✅ Neutral RC override sent!")
    time.sleep(1)
except Exception as e:
    print(f"[ERROR] Failed to send RC override: {e}")

# Test 2: Ramp up channel 3 (vertical thrust)
print()
print("[STEP 4] Testing CHANNEL 3 (Vertical thrust)...")
print("         Ramping from neutral (1500) to full (2000)...")
try:
    for pwm in [1500, 1550, 1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]:
        channels = [1500, 1500, pwm, 1500, 1500, 1500, 1500, 1500]
        vehicle.mav.rc_channels_override_send(
            vehicle.target_system,
            vehicle.target_component,
            *channels
        )
        print(f"    Channel 3: {pwm} PWM", end="\r")
        time.sleep(0.2)
    
    print()
    print("[OK] ✅ Channel 3 test complete!")
    
    # Return to neutral
    neutral_channels = [1500] * 8
    vehicle.mav.rc_channels_override_send(
        vehicle.target_system,
        vehicle.target_component,
        *neutral_channels
    )
    print("    Returned to NEUTRAL")
    
except Exception as e:
    print(f"[ERROR] Channel 3 test failed: {e}")

# Test 3: Test all channels individually
print()
print("[STEP 5] Testing ALL channels individually...")
print("         (Each channel will ramp to 1800 PWM)")
print()

try:
    for ch in range(1, 9):
        print(f"  Testing Channel {ch}...")
        
        # Ramp up
        for pwm in range(1500, 1801, 50):
            channels = [1500] * 8
            channels[ch - 1] = pwm
            vehicle.mav.rc_channels_override_send(
                vehicle.target_system,
                vehicle.target_component,
                *channels
            )
            time.sleep(0.1)
        
        # Return to neutral
        channels = [1500] * 8
        vehicle.mav.rc_channels_override_send(
            vehicle.target_system,
            vehicle.target_component,
            *channels
        )
        
        print(f"    ✅ Channel {ch} OK")
        time.sleep(0.5)
    
    print()
    print("[OK] ✅ All channels tested!")
    
except Exception as e:
    print(f"[ERROR] Channel test failed: {e}")

print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)
print()
print("OBSERVATIONS:")
print("  ✓ If thrusters spun during test: Hardware is working correctly")
print("  ✗ If thrusters didn't spin: Check the following:")
print("    1. Is Pixhawk ARMED? (Check via QGroundControl or MAVProxy)")
print("    2. Are thrusters CONNECTED to Pixhawk outputs?")
print("    3. Do ESCs have power?")
print("    4. Are ArduSub parameters configured for your frame type?")
print()
