"""
UIU MARINER - Find Pixhawk Port
Simple utility to scan and find your Pixhawk connection
Run this on your Raspberry Pi or PC to auto-detect the Pixhawk
"""

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(__file__))

from src.connections.portScanner import PixhawkPortScanner
import json


def update_config(connection_string):
    """Update config.json with discovered connection string."""
    config_path = os.path.join(os.path.dirname(__file__), "config.json")

    try:
        # Load existing config
        with open(config_path, "r") as f:
            config = json.load(f)

        # Update connection string
        config["mavlink_connection"] = connection_string

        # Save back
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

        print(f"[CONFIG] ✅ Updated config.json with: {connection_string}")
        return True

    except Exception as e:
        print(f"[CONFIG] ❌ Failed to update config.json: {e}")
        return False


def main():
    """Run port scanner and optionally update config."""
    print("=" * 70)
    print("UIU MARINER - Pixhawk Port Finder")
    print("=" * 70)
    print()
    print("This tool will scan common serial ports to find your Pixhawk.")
    print("Typical use cases:")
    print("  - Raspberry Pi → Pixhawk (UART/USB)")
    print("  - PC → Pixhawk (USB cable)")
    print()
    print("Make sure your Pixhawk is:")
    print("  ✅ Powered on")
    print("  ✅ Running ArduSub firmware")
    print("  ✅ Connected via UART or USB")
    print()
    input("Press Enter to start scanning...")
    print()

    # Create scanner
    scanner = PixhawkPortScanner()

    # Scan with retry
    result = scanner.scan_with_retry(max_attempts=2, delay=3)

    if result:
        port, baud = result
        connection_string = scanner.get_connection_string(port, baud)

        print()
        print("=" * 70)
        print("✅ SUCCESS! Pixhawk Found!")
        print("=" * 70)
        print(f"   Port:              {port}")
        print(f"   Baud Rate:         {baud}")
        print(f"   Connection String: {connection_string}")
        print("=" * 70)
        print()

        # Ask if user wants to update config
        response = (
            input("Update config.json with this connection? (y/n): ").strip().lower()
        )

        if response == "y":
            if update_config(connection_string):
                print()
                print("✅ Configuration updated successfully!")
                print("   You can now run: python launch_mariner.py")
            else:
                print()
                print("⚠️ Failed to update config. Manual update required:")
                print(f'   "mavlink_connection": "{connection_string}"')
        else:
            print()
            print("ℹ️ To use this connection, update config.json manually:")
            print(f'   "mavlink_connection": "{connection_string}"')

    else:
        print()
        print("=" * 70)
        print("❌ No Pixhawk Found")
        print("=" * 70)
        print()
        print("Troubleshooting Steps:")
        print()
        print("1. Check Physical Connection:")
        print("   - USB cable properly connected")
        print("   - UART TX/RX pins connected correctly")
        print("   - Pixhawk power LED is on")
        print()
        print("2. Verify Firmware:")
        print("   - ArduSub firmware loaded on Pixhawk")
        print("   - Firmware is not stuck in bootloader")
        print()
        print("3. Check Permissions (Linux/Raspberry Pi):")
        print("   sudo usermod -a -G dialout $USER")
        print("   sudo chmod 666 /dev/ttyUSB0")
        print()
        print("4. List Available Ports:")
        print("   Linux: ls -l /dev/tty*")
        print("   Windows: Device Manager → Ports (COM & LPT)")
        print()
        print("5. Test Manually:")
        print("   Linux: screen /dev/ttyUSB0 115200")
        print("   Windows: Use PuTTY or QGroundControl")
        print()
        print("6. Try Network Connection Instead:")
        print("   If using WiFi/Ethernet, use UDP:")
        print('   "mavlink_connection": "udp:192.168.0.104:14550"')
        print("=" * 70)

    print()
    input("Press Enter to exit...")


if __name__ == "__main__":
    main()
