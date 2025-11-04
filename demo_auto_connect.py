#!/usr/bin/env python3
"""
Demo: Auto-Connect Ground Station
Shows how simple it is to use auto-connect
"""

from src.connections.mavlinkConnection import PixhawkConnection
import time
import sys


def main():
    print("=" * 60)
    print(" AUTO-CONNECT DEMO - Ground Station")
    print("=" * 60)
    print()

    # ==========================================
    # THIS IS ALL YOU NEED!
    # ==========================================
    print("Initializing with auto-connect...")
    pixhawk = PixhawkConnection(link="auto")

    print("\nConnecting...")
    if not pixhawk.connect():
        print("\n❌ Connection failed!")
        print("\nTroubleshooting:")
        print("  1. Is Raspberry Pi powered on?")
        print("  2. Is Ethernet cable connected?")
        print("  3. Is Pixhawk connected to Pi via USB?")
        print("\nTest manually: python simple_auto_connect.py")
        sys.exit(1)

    print("\n✅ Connected successfully!")
    print("=" * 60)

    # Now use Pixhawk normally
    print("\n📊 Pixhawk Status:")
    status = pixhawk.get_status()
    print(f"  System ID: {status.get('system_id', 'N/A')}")
    print(f"  Component ID: {status.get('component_id', 'N/A')}")
    print(f"  Connected: {status.get('connected', False)}")

    # Set mode
    print("\n🎮 Setting mode to STABILIZE...")
    if pixhawk.set_mode("STABILIZE"):
        print("  ✅ Mode set")
    else:
        print("  ⚠️  Mode change failed (may need to arm first)")

    # Demonstrate thruster control (safe - all neutral)
    print("\n🔧 Testing thruster commands (neutral position)...")
    print("  Sending 10 neutral commands...")

    for i in range(10):
        # All thrusters at neutral (1500 PWM)
        success = pixhawk.send_rc_channels_override([1500] * 8)
        if success:
            print(f"  Command {i+1}/10 sent", end="\r")
        time.sleep(0.1)

    print("\n  ✅ Commands sent successfully")

    # Cleanup
    print("\n🔌 Disconnecting...")
    pixhawk.close()

    print("\n=" * 60)
    print("✅ DEMO COMPLETE!")
    print("=" * 60)
    print("\nTo use in your code, just do:")
    print("  pixhawk = PixhawkConnection(link='auto')")
    print("  pixhawk.connect()")
    print("\nThat's it! Everything else is automatic! 🎉")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
