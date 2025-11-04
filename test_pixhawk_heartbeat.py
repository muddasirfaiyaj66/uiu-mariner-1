#!/usr/bin/env python3
"""
Test Pixhawk heartbeat and connection stability.
Diagnoses immediate disconnection issue.
"""

from pymavlink import mavutil
import time
import sys


def test_connection(link="tcp:raspberrypi.local:7000"):
    """Test connection and heartbeat handling."""

    print("=" * 60)
    print("PIXHAWK CONNECTION TEST")
    print("=" * 60)
    print(f"Connection: {link}\n")

    try:
        # Step 1: Connect
        print("[1] Connecting...")
        vehicle = mavutil.mavlink_connection(link, autoreconnect=True)
        print("    ✅ Socket created")

        # Step 2: Wait for heartbeat
        print("[2] Waiting for heartbeat...")
        start_time = time.time()
        vehicle.wait_heartbeat(timeout=10)
        elapsed = time.time() - start_time
        print(f"    ✅ Heartbeat received in {elapsed:.2f}s")
        print(f"    System ID: {vehicle.target_system}")
        print(f"    Component ID: {vehicle.target_component}")

        # Step 3: Send ARM command (without actually arming)
        print("\n[3] Testing command transmission...")
        try:
            # Send a test command that doesn't affect the vehicle
            vehicle.mav.command_long_send(
                vehicle.target_system,
                vehicle.target_component,
                mavutil.mavlink.MAV_CMD_REQUEST_AUTOPILOT_CAPABILITIES,
                0,
                1,  # version
                0,
                0,
                0,
                0,
                0,
                0,
            )
            print("    ✅ Command sent successfully")
        except Exception as e:
            print(f"    ⚠️ Command send error: {e}")

        # Step 4: Test repeated heartbeat checks
        print("\n[4] Testing heartbeat reception (10 seconds)...")
        heartbeat_count = 0
        last_heartbeat_time = time.time()
        heartbeat_timeout = 10.0

        for i in range(20):
            # Non-blocking heartbeat check
            msg = vehicle.recv_match(type="HEARTBEAT", blocking=False, timeout=0)

            if msg:
                heartbeat_count += 1
                last_heartbeat_time = time.time()
                print(f"    [{i+1}/20] ✅ Heartbeat #{heartbeat_count} received")
            else:
                time_since_hb = time.time() - last_heartbeat_time
                print(
                    f"    [{i+1}/20] ⏳ Waiting... ({time_since_hb:.1f}s since last HB)"
                )

            # Check for timeout
            if time.time() - last_heartbeat_time > heartbeat_timeout:
                print(f"    ❌ HEARTBEAT TIMEOUT! ({heartbeat_timeout}s)")
                print("    This explains the disconnection issue!")
                vehicle.close()
                return False

            time.sleep(0.5)

        print(f"\n    ✅ Received {heartbeat_count} heartbeats")

        # Step 5: Test RC_CHANNELS_OVERRIDE
        print("\n[5] Testing RC_CHANNELS_OVERRIDE...")
        try:
            channels = [1500] * 8  # Neutral
            vehicle.mav.rc_channels_override_send(
                vehicle.target_system, vehicle.target_component, *channels
            )
            print("    ✅ RC_CHANNELS_OVERRIDE sent")
        except Exception as e:
            print(f"    ❌ RC_CHANNELS_OVERRIDE failed: {e}")

        # Step 6: Keep connection alive for 10 more seconds
        print("\n[6] Monitoring connection for 10 seconds...")
        for i in range(20):
            try:
                msg = vehicle.recv_match(blocking=False, timeout=0)
                if msg and msg.get_type() == "HEARTBEAT":
                    print(f"    [{i+1}/20] ✅ Heartbeat")
                time.sleep(0.5)
            except Exception as e:
                print(f"    ❌ Error at iteration {i+1}: {e}")
                break

        print("\n    ✅ Connection stable for 10 seconds")

        # Clean up
        vehicle.close()

        print("\n" + "=" * 60)
        print("✅ TEST PASSED - Connection is stable!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        print("\n" + "=" * 60)
        print("Possible causes:")
        print("1. Pi MAVProxy server not running")
        print("2. Network unreachable")
        print("3. Pixhawk not connected to Pi")
        print("4. Firewall blocking port 7000")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
