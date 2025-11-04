#!/usr/bin/env python3
"""
🚀 DIRECT THRUSTER TEST (Run on Raspberry Pi)
==============================================
This script tests thrusters directly on the Pi, bypassing network issues.

Usage:
    ssh pi@raspberrypi.local
    python3 test_thruster_direct.py
"""

from pymavlink import mavutil
import time
import sys


def test_thrusters_direct():
    """Test thrusters directly connected to Pixhawk."""
    print("=" * 70)
    print("🚀 DIRECT THRUSTER TEST - Running on Raspberry Pi")
    print("=" * 70)
    print()

    print("⚠️  WARNING: This will spin the thrusters!")
    print("Make sure the ROV is:")
    print("  - In water, or")
    print("  - Secured on a stand, or")
    print("  - Propellers removed")
    print()

    response = input("Continue? (yes/no): ").strip().lower()
    if response != "yes":
        print("Aborted.")
        return

    print()
    print("🔌 Connecting to Pixhawk...")

    # Auto-detect the correct serial port
    import glob

    ports = glob.glob("/dev/ttyACM*")

    if not ports:
        print("   ❌ No /dev/ttyACM* ports found!")
        print()
        print("Troubleshooting:")
        print("  - Check USB cable connection")
        print("  - Check if Pixhawk is powered")
        print("  - Run: ls -la /dev/tty* | grep ACM")
        return

    print(f"   Found ports: {', '.join(ports)}")

    master = None
    for port in ports:
        try:
            print(f"   Trying {port}...")
            master = mavutil.mavlink_connection(port, baud=115200)
            print("   Waiting for heartbeat...")
            master.wait_heartbeat(timeout=3)
            print(f"   ✅ Connected to {port}! System ID: {master.target_system}")
            print()
            break
        except Exception as e:
            print(f"   ❌ Failed on {port}: {e}")
            master = None

    if not master:
        print()
        print("   ❌ Could not connect to any serial port!")
        print()
        print("Troubleshooting:")
        print("  - Check USB cable connection")
        print("  - Check if Pixhawk is powered")
        print("  - Check if another program is using the port")
        print("  - Run: sudo lsof | grep ttyACM")
        return

    # Check current armed status
    print("📊 Checking current status...")
    msg = master.recv_match(type="HEARTBEAT", blocking=True, timeout=3)
    if msg:
        armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        mode = msg.custom_mode

        mode_names = {
            0: "STABILIZE",
            1: "ACRO",
            2: "ALT_HOLD",
            3: "AUTO",
            4: "GUIDED",
            7: "CIRCLE",
            9: "SURFACE",
            16: "POSHOLD",
            19: "MANUAL",
        }
        mode_name = mode_names.get(mode, f"UNKNOWN({mode})")

        print(f"   Mode: {mode_name}")
        print(f"   Armed: {'✅ YES' if armed else '❌ NO'}")
        print()

        if not armed:
            print("⚠️  Pixhawk is DISARMED - arming now...")
            master.arducopter_arm()
            master.motors_armed_wait()
            print("   ✅ Armed!")
            print()

    # Test sequence
    print("🧪 Testing Thruster Channels...")
    print("-" * 70)
    print()

    neutral = [1500] * 8

    tests = [
        (
            "Channel 1 (Pin 1) - Forward Thruster",
            [1600, 1500, 1500, 1500, 1500, 1500, 1500, 1500],
        ),
        (
            "Channel 2 (Pin 2) - Lateral Thruster",
            [1500, 1600, 1500, 1500, 1500, 1500, 1500, 1500],
        ),
        (
            "Channel 3 (Pin 3) - Vertical Thruster",
            [1500, 1500, 1600, 1500, 1500, 1500, 1500, 1500],
        ),
        (
            "Channel 8 (Pin 8) - Rear Thruster",
            [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1600],
        ),
    ]

    for test_name, channels in tests:
        print(f"   Testing: {test_name}")
        print(f"   Sending: {channels}")

        try:
            master.mav.rc_channels_override_send(
                master.target_system, master.target_component, *channels
            )
            print("   ✅ Command sent")

            # Monitor servo output
            time.sleep(0.1)
            servo_msg = master.recv_match(
                type="SERVO_OUTPUT_RAW", blocking=True, timeout=1
            )
            if servo_msg:
                print(
                    f"   📊 Servo outputs: {servo_msg.servo1_raw} {servo_msg.servo2_raw} {servo_msg.servo3_raw} {servo_msg.servo4_raw} {servo_msg.servo5_raw} {servo_msg.servo6_raw} {servo_msg.servo7_raw} {servo_msg.servo8_raw}"
                )

            print("   Waiting 2 seconds...")
            time.sleep(2)

            # Return to neutral
            master.mav.rc_channels_override_send(
                master.target_system, master.target_component, *neutral
            )
            print("   ✅ Returned to neutral")
            print()

        except Exception as e:
            print(f"   ❌ Error: {e}")
            print()

    # Disarm
    print("🛑 Disarming...")
    master.mav.rc_channels_override_send(
        master.target_system, master.target_component, *neutral
    )
    time.sleep(0.5)
    master.arducopter_disarm()
    print("   ✅ Disarmed")
    print()

    print("=" * 70)
    print("📝 RESULTS")
    print("=" * 70)
    print()
    print("If thrusters DID NOT spin:")
    print("  1. Check ESC power (battery connected?)")
    print("  2. Check ESC calibration")
    print("  3. Verify wiring (Pixhawk MAIN OUT → ESC signal)")
    print("  4. Check Pixhawk parameters (MOT_PWM_MIN/MAX)")
    print("  5. Check if servo outputs changed (in log above)")
    print()
    print("If thrusters DID spin:")
    print("  ✅ Hardware works!")
    print("  Problem is in the Windows → Pi → Pixhawk connection chain")
    print()


if __name__ == "__main__":
    try:
        test_thrusters_direct()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
