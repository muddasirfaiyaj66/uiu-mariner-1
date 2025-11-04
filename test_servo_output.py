#!/usr/bin/env python3
"""
Diagnostic script to verify Pixhawk is receiving and processing RC_CHANNELS_OVERRIDE commands.
Checks if the Pixhawk's RC output channels are changing when we send commands.
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

from src.connections.mavlinkConnection import PixhawkConnection


def check_rc_output_channels():
    """Monitor RC output channels to verify Pixhawk is processing our commands."""

    print("=" * 70)
    print("PIXHAWK RC OUTPUT CHANNEL DIAGNOSTIC")
    print("=" * 70)

    # Connect to Pixhawk
    print("\n[1] Connecting to Pixhawk...")
    pixhawk = PixhawkConnection(link="tcp:raspberrypi.local:7000", auto_detect=False)

    if not pixhawk.connect():
        print("[❌] Failed to connect to Pixhawk")
        return False

    print("[✅] Connected")

    # Set mode to MANUAL
    print("\n[2] Setting mode to MANUAL...")
    pixhawk.set_mode("MANUAL")
    time.sleep(1)

    # ARM
    print("\n[3] Arming Pixhawk...")
    pixhawk.arm()
    time.sleep(1)

    # Now send RC commands and monitor for SERVO_OUTPUT_RAW messages
    print("\n[4] Sending RC commands and monitoring servo outputs...")
    print("    Watch for 'servo1' through 'servo8' values changing\n")

    test_commands = [
        ("Neutral", [1500] * 8),
        ("Forward", [1875, 1500, 1500, 1500, 1500, 1500, 1500, 1875]),
        ("Yaw Left", [1500, 1000, 1500, 1500, 1500, 1500, 1500, 1500]),
        ("Up", [1500, 1500, 1875, 1875, 1500, 1875, 1875, 1500]),
    ]

    for name, channels in test_commands:
        print(f"\n    Testing: {name}")
        print(f"    Sending: {channels}")

        # Send command
        if not pixhawk.send_rc_channels_override(channels):
            print(f"    ❌ Failed to send")
            continue

        # Monitor SERVO_OUTPUT_RAW for 3 seconds
        print(f"    Monitoring servo outputs...")
        servo_data_found = False
        start_time = time.time()

        while time.time() - start_time < 3:
            try:
                # Try to receive SERVO_OUTPUT_RAW message
                msg = pixhawk.vehicle.recv_match(
                    type="SERVO_OUTPUT_RAW", blocking=False, timeout=0
                )

                if msg:
                    servo_data_found = True
                    # Extract servo pulse widths (microseconds)
                    servos = [
                        msg.servo1_raw,
                        msg.servo2_raw,
                        msg.servo3_raw,
                        msg.servo4_raw,
                        msg.servo5_raw,
                        msg.servo6_raw,
                        msg.servo7_raw,
                        msg.servo8_raw,
                    ]

                    print(f"    ✅ SERVO OUTPUT: {servos}")

                    # Check if servo values match our RC command (approximately)
                    match_count = 0
                    for i, (cmd, servo) in enumerate(zip(channels, servos), 1):
                        # Allow ±100us tolerance
                        if abs(servo - cmd) < 100:
                            match_count += 1

                    print(f"    ✓ Channels matching: {match_count}/8")

                    if match_count >= 6:
                        print(f"    ✅ Commands are being forwarded to servos!")
                    else:
                        print(f"    ⚠️ Some channels not matching (check mapping)")

                    time.sleep(0.5)
                else:
                    time.sleep(0.1)

            except Exception as e:
                print(f"    ⚠️ Error reading servo: {e}")
                time.sleep(0.1)

        if not servo_data_found:
            print(f"    ❌ NO SERVO OUTPUT DETECTED!")
            print(f"       Pixhawk is NOT forwarding RC commands to ESCs")
            print(f"       Possible causes:")
            print(f"       - Pixhawk firmware is not ArduSub")
            print(f"       - Pixhawk serial port not connected properly")
            print(f"       - RC output not configured in Pixhawk parameters")

    # Disarm
    print("\n[5] Disarming...")
    pixhawk.disarm()
    pixhawk.close()

    print("\n" + "=" * 70)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 70)

    return True


if __name__ == "__main__":
    try:
        check_rc_output_channels()
    except KeyboardInterrupt:
        print("\n\n[⚠️] Interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n[❌] Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
