#!/usr/bin/env python3
"""
Test script to arm Pixhawk and spin all thrusters.
Connects to Pixhawk, arms it, and sends thruster commands.
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from src.connections.mavlinkConnection import PixhawkConnection


def test_thruster_control():
    """Test thruster control: connect, arm, and spin."""

    print("=" * 60)
    print("THRUSTER CONTROL TEST")
    print("=" * 60)

    # Connect to Pixhawk
    print("\n[1] Connecting to Pixhawk...")
    pixhawk = PixhawkConnection(link="tcp:raspberrypi.local:7000", auto_detect=False)

    if not pixhawk.connect():
        print("[❌] Failed to connect to Pixhawk")
        return False

    print("[✅] Connected to Pixhawk")
    print(f"    System ID: {pixhawk.vehicle.target_system}")
    print(f"    Component ID: {pixhawk.vehicle.target_component}")

    # Check current mode
    print("\n[2] Checking current mode...")
    try:
        # Read system status
        pixhawk.vehicle.wait_heartbeat(timeout=2)
        print("[✅] Heartbeat confirmed")
    except:
        print("[⚠️] No heartbeat, but continuing...")

    # Set mode to MANUAL (required for RC override)
    print("\n[3] Setting mode to MANUAL...")
    if pixhawk.set_mode("MANUAL"):
        print("[✅] Mode set to MANUAL")
    else:
        print("[⚠️] Could not set mode (this is OK)")

    time.sleep(1)

    # ARM the vehicle
    print("\n[4] ARMING thrusters...")
    if pixhawk.arm():
        print("[✅] ARMED!")
    else:
        print("[❌] Failed to arm")
        pixhawk.close()
        return False

    time.sleep(2)

    # Test thruster control - all thrusters forward
    print("\n[5] Testing thruster control...")
    print("    Sending: All thrusters at 75% forward")

    # Channel values: 1500 = neutral, 1875 = 75% forward, 1125 = 75% reverse
    forward_channels = [1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875]

    for i in range(5):
        print(f"\n    Iteration {i+1}/5:")

        if pixhawk.send_rc_channels_override(forward_channels):
            print(f"    ✅ Sent → {forward_channels}")
        else:
            print(f"    ❌ Send failed!")
            break

        time.sleep(0.5)

    # Test different thruster combinations
    print("\n[6] Testing individual thrust directions...")

    test_cases = [
        ("Forward", [1875, 1500, 1500, 1500, 1500, 1500, 1500, 1875]),
        ("Reverse", [1125, 1500, 1500, 1500, 1500, 1500, 1500, 1125]),
        ("Yaw Left", [1500, 1125, 1500, 1500, 1500, 1500, 1500, 1500]),
        ("Yaw Right", [1500, 1875, 1500, 1500, 1500, 1500, 1500, 1500]),
        ("Up", [1500, 1500, 1875, 1875, 1500, 1875, 1875, 1500]),
        ("Down", [1500, 1500, 1125, 1125, 1500, 1125, 1125, 1500]),
        ("All Neutral", [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]),
    ]

    for name, channels in test_cases:
        print(f"\n    {name}:")
        if pixhawk.send_rc_channels_override(channels):
            print(f"    ✅ Sent → Ch{list(range(1,9))}")
        else:
            print(f"    ❌ Failed")
        time.sleep(0.5)

    # Disarm
    print("\n[7] DISARMING thrusters...")
    if pixhawk.disarm():
        print("[✅] DISARMED")
    else:
        print("[⚠️] Could not disarm (not critical)")

    # Close connection
    pixhawk.close()

    print("\n" + "=" * 60)
    print("✅ THRUSTER TEST COMPLETE")
    print("=" * 60)
    print("\nIf all thrusters spun as expected:")
    print("✅ The control system is working!")
    print("\nIf thrusters didn't spin:")
    print("❌ Check:")
    print("   1. Pixhawk firmware is ArduSub")
    print("   2. ESCs are armed (red light on Pi)")
    print("   3. RC channel mapping in ArduSub is correct")
    print("   4. Power is connected to thrusters")
    print("   5. Thruster calibration is complete")

    return True


if __name__ == "__main__":
    try:
        success = test_thruster_control()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n[⚠️] Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[❌] Test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
