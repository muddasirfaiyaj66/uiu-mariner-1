#!/usr/bin/env python3
"""
Test MAVLink Connection Stability
Verifies connection stays alive without disconnecting
"""

import sys
import os
import time

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from connections.mavlinkConnection import PixhawkConnection


def test_stable_connection():
    """Test that connection stays alive for extended period."""
    print("=" * 60)
    print("MAVLink Connection Stability Test")
    print("=" * 60)
    print()

    # Create connection
    print("[1] Connecting to Pixhawk...")
    pixhawk = PixhawkConnection(link="tcp:raspberrypi.local:7000", auto_detect=False)

    if not pixhawk.connect():
        print("[❌] Failed to connect")
        return False

    print("[✅] Connected successfully")
    print()

    # Monitor connection for 30 seconds
    print("[2] Monitoring connection stability for 30 seconds...")
    print("    (Press Ctrl+C to stop early)")
    print()

    start_time = time.time()
    check_count = 0
    disconnect_count = 0

    try:
        while time.time() - start_time < 30:
            # Check connection status
            status = pixhawk.get_status()
            check_count += 1

            if status["connected"]:
                print(
                    f"[{check_count:3d}] ✅ Connected | Heartbeat age: {status['last_heartbeat']:.1f}s",
                    end="\r",
                )
            else:
                disconnect_count += 1
                print(
                    f"[{check_count:3d}] ❌ DISCONNECTED                                           "
                )

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[⚠️] Stopped by user")

    print("\n")
    print("=" * 60)
    print("RESULTS")
    print("=" * 60)
    print(f"Total checks: {check_count}")
    print(f"Disconnections: {disconnect_count}")

    if disconnect_count == 0:
        print("[✅] Connection remained stable!")
        success = True
    else:
        print(f"[❌] Connection unstable - {disconnect_count} disconnections")
        success = False

    # Cleanup
    pixhawk.close()

    return success


if __name__ == "__main__":
    success = test_stable_connection()
    sys.exit(0 if success else 1)
