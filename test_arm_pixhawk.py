#!/usr/bin/env python3
"""
Test script to verify Pixhawk arming and thruster control.
This will help diagnose why thrusters aren't working.
"""

from pymavlink import mavutil
import time


def connect_pixhawk(link="tcp:raspberrypi.local:7000"):
    """Connect to Pixhawk via MAVProxy."""
    print(f"[1] Connecting to {link}...")
    vehicle = mavutil.mavlink_connection(link)

    print("[2] Waiting for heartbeat...")
    vehicle.wait_heartbeat(timeout=10)
    print(
        f"✅ Connected! System ID: {vehicle.target_system}, Component ID: {vehicle.target_component}"
    )

    return vehicle


def check_mode(vehicle):
    """Check current flight mode."""
    print("\n[3] Requesting current mode...")
    vehicle.mav.request_data_stream_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL,
        1,  # Hz
        1,  # Enable
    )

    # Wait for HEARTBEAT message with mode info
    msg = vehicle.recv_match(type="HEARTBEAT", blocking=True, timeout=5)
    if msg:
        mode = mavutil.mode_string_v10(msg)
        print(f"✅ Current mode: {mode}")
        print(f"   Base mode: {msg.base_mode}")
        print(f"   Custom mode: {msg.custom_mode}")
        print(f"   System status: {msg.system_status}")
        return mode
    else:
        print("❌ No heartbeat received")
        return None


def set_mode(vehicle, mode_name="MANUAL"):
    """Set flight mode."""
    print(f"\n[4] Setting mode to {mode_name}...")

    # Get mode ID
    if mode_name not in vehicle.mode_mapping():
        print(f"❌ Unknown mode: {mode_name}")
        print(f"Available modes: {list(vehicle.mode_mapping().keys())}")
        return False

    mode_id = vehicle.mode_mapping()[mode_name]

    vehicle.mav.set_mode_send(
        vehicle.target_system,
        mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED,
        mode_id,
    )

    # Wait for confirmation
    time.sleep(1)

    msg = vehicle.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
    if msg:
        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print(f"✅ Mode changed to {mode_name}")
            return True
        else:
            print(f"❌ Mode change failed: {msg.result}")
            return False
    else:
        print("⚠️  No acknowledgment received, mode may have changed anyway")
        return True


def arm_vehicle(vehicle):
    """Arm the vehicle."""
    print("\n[5] Arming vehicle...")

    vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,  # confirmation
        1,  # arm
        0,
        0,
        0,
        0,
        0,
        0,
    )

    # Wait for confirmation
    msg = vehicle.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
    if msg:
        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("✅ Vehicle ARMED!")
            return True
        else:
            print(f"❌ Arming FAILED!")
            print(f"   Result code: {msg.result}")
            print(f"   Common reasons:")
            print(f"   - Not in MANUAL mode")
            print(f"   - Pre-arm checks failing")
            print(f"   - Safety switch not pressed (if applicable)")
            return False
    else:
        print("❌ No acknowledgment received for arm command")
        return False


def check_arm_status(vehicle):
    """Check if vehicle is armed."""
    print("\n[6] Checking arm status...")

    msg = vehicle.recv_match(type="HEARTBEAT", blocking=True, timeout=3)
    if msg:
        armed = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        if armed:
            print("✅ Vehicle is ARMED")
        else:
            print("⚠️  Vehicle is DISARMED")
        return bool(armed)
    else:
        print("❌ Could not check arm status")
        return False


def test_thrusters(vehicle):
    """Send a test thruster command."""
    print("\n[7] Sending test thruster command...")
    print("    (All thrusters neutral = 1500μs)")

    # Neutral position
    channels = [1500] * 8

    vehicle.mav.rc_channels_override_send(
        vehicle.target_system, vehicle.target_component, *channels
    )

    print("✅ Test command sent")
    time.sleep(2)

    # Try a small vertical movement
    print("\n[8] Testing vertical thrusters...")
    print("    (Slightly up = Ch3,Ch4=1450, Ch6,Ch7=1550)")

    channels = [1500, 1500, 1450, 1450, 1500, 1550, 1550, 1500]
    vehicle.mav.rc_channels_override_send(
        vehicle.target_system, vehicle.target_component, *channels
    )

    print("✅ Vertical test command sent")
    print("⚠️  CHECK IF THRUSTERS ARE MOVING!")
    time.sleep(3)

    # Back to neutral
    print("\n[9] Returning to neutral...")
    channels = [1500] * 8
    vehicle.mav.rc_channels_override_send(
        vehicle.target_system, vehicle.target_component, *channels
    )
    print("✅ Neutral command sent")


def disarm_vehicle(vehicle):
    """Disarm the vehicle."""
    print("\n[10] Disarming vehicle...")

    vehicle.mav.command_long_send(
        vehicle.target_system,
        vehicle.target_component,
        mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
        0,  # confirmation
        0,  # disarm
        0,
        0,
        0,
        0,
        0,
        0,
    )

    msg = vehicle.recv_match(type="COMMAND_ACK", blocking=True, timeout=3)
    if msg:
        if msg.result == mavutil.mavlink.MAV_RESULT_ACCEPTED:
            print("✅ Vehicle disarmed")
            return True
        else:
            print(f"⚠️  Disarm result: {msg.result}")
            return False
    else:
        print("⚠️  No acknowledgment for disarm command")
        return False


def main():
    """Run the full test sequence."""
    print("=" * 60)
    print("PIXHAWK ARM & THRUSTER TEST")
    print("=" * 60)

    try:
        # Connect
        vehicle = connect_pixhawk()

        # Check current mode
        mode = check_mode(vehicle)

        # Set to MANUAL mode if not already
        if mode != "MANUAL":
            set_mode(vehicle, "MANUAL")

        # Arm the vehicle
        if arm_vehicle(vehicle):
            # Verify arm status
            time.sleep(1)
            is_armed = check_arm_status(vehicle)

            if is_armed:
                # Test thrusters
                test_thrusters(vehicle)

                # Disarm
                time.sleep(2)
                disarm_vehicle(vehicle)
            else:
                print("\n❌ Vehicle failed to arm!")
                print("    Check the following:")
                print("    1. Is the Pixhawk in MANUAL mode?")
                print("    2. Are there any pre-arm check failures?")
                print("    3. Is the safety switch enabled (if present)?")
        else:
            print("\n❌ Could not arm vehicle!")
            print("    Try manually setting MANUAL mode first")

        print("\n" + "=" * 60)
        print("Test complete!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
