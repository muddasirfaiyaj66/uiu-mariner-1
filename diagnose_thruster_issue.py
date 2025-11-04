#!/usr/bin/env python3
"""
🔍 THRUSTER ISSUE DIAGNOSTIC
==============================
This script diagnoses why thrusters aren't working in live tests.

It checks:
1. Pixhawk connection
2. Flight mode
3. Arming status
4. RC_CHANNELS_OVERRIDE reception
5. Motor output configuration
6. Safety switches
"""

import sys
import time
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from connections.mavlinkConnection import PixhawkConnection
import json


def read_config():
    """Read connection config."""
    config_path = Path(__file__).parent / "config.json"
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            return config.get("mavlink_connection", "tcp:raspberrypi.local:7000")
    return "tcp:raspberrypi.local:7000"


def check_pixhawk_params(pixhawk):
    """Check critical Pixhawk parameters."""
    print("\n📋 Checking Pixhawk Parameters...")
    print("-" * 70)

    # Important parameters for thruster control
    params_to_check = [
        ("ARMING_CHECK", "Arming safety checks"),
        ("BRD_SAFETY_DEFLT", "Safety switch requirement"),
        ("MOT_PWM_MIN", "Minimum PWM output"),
        ("MOT_PWM_MAX", "Maximum PWM output"),
        ("FRAME_CONFIG", "Frame configuration"),
        ("RC1_MIN", "RC Channel 1 min"),
        ("RC1_MAX", "RC Channel 1 max"),
    ]

    for param_name, description in params_to_check:
        try:
            # Request parameter
            pixhawk.vehicle.mav.param_request_read_send(
                pixhawk.vehicle.target_system,
                pixhawk.vehicle.target_component,
                param_name.encode("utf-8"),
                -1,
            )

            # Wait for response
            msg = pixhawk.vehicle.recv_match(
                type="PARAM_VALUE", blocking=True, timeout=2
            )
            if msg and msg.param_id == param_name:
                print(
                    f"   ✓ {param_name:20s} = {msg.param_value:10.2f}  ({description})"
                )
            else:
                print(f"   ⚠️ {param_name:20s} - No response ({description})")
        except Exception as e:
            print(f"   ❌ {param_name:20s} - Error: {e}")

    print()


def check_servo_outputs(pixhawk):
    """Monitor SERVO_OUTPUT_RAW messages."""
    print("\n🔌 Monitoring Servo Outputs (5 seconds)...")
    print("-" * 70)
    print("This shows the actual PWM values being output on MAIN OUT pins.")
    print("Expected: 1500μs when neutral, different values when commanded")
    print()

    start_time = time.time()
    last_print = 0

    while time.time() - start_time < 5:
        msg = pixhawk.vehicle.recv_match(
            type="SERVO_OUTPUT_RAW", blocking=False, timeout=0.1
        )

        if msg and time.time() - last_print > 0.5:
            print(f"   SERVO_OUTPUT_RAW:")
            print(
                f"      Ch1-4:  {msg.servo1_raw:4d}  {msg.servo2_raw:4d}  {msg.servo3_raw:4d}  {msg.servo4_raw:4d}"
            )
            print(
                f"      Ch5-8:  {msg.servo5_raw:4d}  {msg.servo6_raw:4d}  {msg.servo7_raw:4d}  {msg.servo8_raw:4d}"
            )
            print()
            last_print = time.time()

    print()


def test_rc_override_reception(pixhawk):
    """Test if Pixhawk is receiving RC_CHANNELS_OVERRIDE."""
    print("\n📡 Testing RC_CHANNELS_OVERRIDE Reception...")
    print("-" * 70)

    # Send a test pattern
    test_channels = [1600, 1400, 1700, 1300, 1600, 1400, 1700, 1300]

    print(f"   Sending test pattern: {test_channels}")
    print("   If thrusters work, SERVO_OUTPUT_RAW should change...")
    print()

    # Send the command
    try:
        pixhawk.vehicle.mav.rc_channels_override_send(
            pixhawk.vehicle.target_system,
            pixhawk.vehicle.target_component,
            *test_channels,
        )
        print("   ✓ Command sent successfully")
    except Exception as e:
        print(f"   ❌ Failed to send: {e}")
        return False

    # Monitor outputs for 3 seconds
    print()
    print("   Monitoring outputs for 3 seconds...")
    start_time = time.time()
    last_print = 0

    while time.time() - start_time < 3:
        msg = pixhawk.vehicle.recv_match(
            type="SERVO_OUTPUT_RAW", blocking=False, timeout=0.1
        )

        if msg and time.time() - last_print > 0.5:
            print(
                f"      Ch1-4:  {msg.servo1_raw:4d}  {msg.servo2_raw:4d}  {msg.servo3_raw:4d}  {msg.servo4_raw:4d}"
            )
            print(
                f"      Ch5-8:  {msg.servo5_raw:4d}  {msg.servo6_raw:4d}  {msg.servo7_raw:4d}  {msg.servo8_raw:4d}"
            )
            last_print = time.time()

    # Return to neutral
    neutral = [1500] * 8
    pixhawk.vehicle.mav.rc_channels_override_send(
        pixhawk.vehicle.target_system, pixhawk.vehicle.target_component, *neutral
    )

    print()
    print("   ✓ Returned to neutral")
    print()

    return True


def check_mode_and_arming(pixhawk):
    """Check current mode and arming status."""
    print("\n⚙️  Flight Mode & Arming Status...")
    print("-" * 70)

    # Wait for heartbeat to get mode
    msg = pixhawk.vehicle.recv_match(type="HEARTBEAT", blocking=True, timeout=5)

    if msg:
        # Decode mode
        mode = msg.custom_mode
        armed = msg.base_mode & 128  # MAV_MODE_FLAG_SAFETY_ARMED

        # ArduSub modes
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
        armed_status = "✅ ARMED" if armed else "❌ DISARMED"

        print(f"   Flight Mode: {mode_name}")
        print(f"   Armed Status: {armed_status}")
        print()

        if not armed:
            print("   ⚠️  WARNING: Pixhawk is DISARMED!")
            print("   Thrusters will NOT work unless armed.")
            print()

            response = input("   Do you want to ARM now? (y/n): ").strip().lower()
            if response == "y":
                print("   Arming...")
                if pixhawk.arm():
                    print("   ✅ Armed successfully!")
                else:
                    print("   ❌ Failed to arm")
                print()

        if mode_name not in ["STABILIZE", "MANUAL", "ALT_HOLD"]:
            print(f"   ⚠️  WARNING: Mode is {mode_name}")
            print("   For manual thruster control, use STABILIZE or MANUAL mode.")
            print()
    else:
        print("   ❌ No heartbeat received")
        print()


def check_rc_channels_override_status(pixhawk):
    """Check RC_CHANNELS_OVERRIDE status."""
    print("\n📊 RC Input Status...")
    print("-" * 70)

    # Monitor RC_CHANNELS messages
    print("   Waiting for RC_CHANNELS message...")
    msg = pixhawk.vehicle.recv_match(type="RC_CHANNELS", blocking=True, timeout=5)

    if msg:
        print(f"   ✓ RC_CHANNELS received")
        print(
            f"      Ch1-4:  {msg.chan1_raw:4d}  {msg.chan2_raw:4d}  {msg.chan3_raw:4d}  {msg.chan4_raw:4d}"
        )
        print(
            f"      Ch5-8:  {msg.chan5_raw:4d}  {msg.chan6_raw:4d}  {msg.chan7_raw:4d}  {msg.chan8_raw:4d}"
        )
        print()

        # Check if values are at neutral (1500) or show variation
        channels = [
            msg.chan1_raw,
            msg.chan2_raw,
            msg.chan3_raw,
            msg.chan4_raw,
            msg.chan5_raw,
            msg.chan6_raw,
            msg.chan7_raw,
            msg.chan8_raw,
        ]

        if all(ch == 0 for ch in channels):
            print("   ⚠️  WARNING: All channels are 0!")
            print("   This means NO RC input is being received.")
            print()
        elif all(abs(ch - 1500) < 10 for ch in channels if ch != 0):
            print("   ℹ️  All channels at neutral (1500μs)")
            print("   This is normal when no commands are being sent.")
            print()
    else:
        print("   ❌ No RC_CHANNELS message received")
        print()


def main():
    """Main diagnostic routine."""
    print("=" * 70)
    print("🔍 THRUSTER ISSUE DIAGNOSTIC - UIU MARINER")
    print("=" * 70)

    # Connect to Pixhawk
    connection_string = read_config()
    print(f"\n🔌 Connecting to Pixhawk: {connection_string}")

    pixhawk = PixhawkConnection(link=connection_string, auto_detect=True)
    if not pixhawk.connect():
        print("\n❌ FAILED: Cannot connect to Pixhawk")
        print("\nTroubleshooting:")
        print("   1. Check if Raspberry Pi is powered on")
        print("   2. Check network: ping raspberrypi.local")
        print("   3. Check if MAVProxy is running on Pi")
        print("   4. Try: ssh pi@raspberrypi.local")
        return

    print("✅ Connected!\n")

    # Run diagnostic checks
    try:
        check_mode_and_arming(pixhawk)
        check_rc_channels_override_status(pixhawk)
        check_servo_outputs(pixhawk)
        test_rc_override_reception(pixhawk)
        check_pixhawk_params(pixhawk)

        # Final summary
        print("\n" + "=" * 70)
        print("📝 DIAGNOSTIC SUMMARY")
        print("=" * 70)
        print()
        print("Common issues and solutions:")
        print()
        print("1. DISARMED:")
        print("   Solution: Arm the Pixhawk before sending thruster commands")
        print()
        print("2. SERVO_OUTPUT_RAW shows 0 or doesn't change:")
        print("   Solution: Check MOT_PWM_MIN/MAX parameters")
        print("   Solution: Check if safety switch is enabled (BRD_SAFETY_DEFLT)")
        print()
        print("3. RC_CHANNELS shows 0 or not updating:")
        print("   Solution: Check RC input mode (should accept RC_OVERRIDE)")
        print("   Solution: Verify ArduSub parameter SYSID_MYGCS")
        print()
        print("4. Wrong flight mode:")
        print("   Solution: Switch to STABILIZE or MANUAL mode")
        print()
        print("5. ESCs not calibrated:")
        print("   Solution: Calibrate ESCs with ArduSub calibration routine")
        print()
        print("6. Power issues:")
        print("   Solution: Check if ESCs and thrusters are powered")
        print("   Solution: Verify battery voltage is adequate")
        print()

    except KeyboardInterrupt:
        print("\n\n⚠️  Diagnostic interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during diagnostic: {e}")
        import traceback

        traceback.print_exc()
    finally:
        pixhawk.close()
        print("\n✅ Diagnostic complete!")


if __name__ == "__main__":
    main()
