#!/usr/bin/env python3
"""
Test BMP388 Sensor on Raspberry Pi
Quick diagnostic to verify sensor is connected and working
"""

import sys
import time

try:
    import smbus
except ImportError:
    print("❌ Error: smbus library not installed")
    print("   Install with: sudo apt-get install python3-smbus")
    sys.exit(1)

# BMP388 I2C address (default: 0x77 or 0x76)
BMP388_ADDRESS = 0x77
I2C_BUS = 1  # Usually bus 1 on Raspberry Pi


def test_bmp388():
    print("🔍 Testing BMP388 Sensor...")
    print("=" * 50)

    try:
        # Initialize I2C bus
        bus = smbus.SMBus(I2C_BUS)
        print(f"✅ I2C bus {I2C_BUS} opened successfully")

        # Try to read chip ID (register 0x00)
        chip_id = bus.read_byte_data(BMP388_ADDRESS, 0x00)
        print(f"✅ BMP388 found at address 0x{BMP388_ADDRESS:02X}")
        print(f"   Chip ID: 0x{chip_id:02X} (should be 0x50 for BMP388)")

        if chip_id == 0x50:
            print("\n✅ SUCCESS: BMP388 sensor is working correctly!")

            # Try reading some registers to show it's responsive
            print("\n📊 Reading sensor registers...")
            print(
                "   Status Register: 0x{:02X}".format(
                    bus.read_byte_data(BMP388_ADDRESS, 0x03)
                )
            )
            print(
                "   Power Control:   0x{:02X}".format(
                    bus.read_byte_data(BMP388_ADDRESS, 0x1B)
                )
            )

            print("\n💡 Next step: Run pi_sensor_server.py to start streaming data")
            return True
        else:
            print(
                f"\n⚠️  WARNING: Chip ID mismatch (expected 0x50, got 0x{chip_id:02X})"
            )
            print("   This might not be a BMP388 sensor")
            return False

    except FileNotFoundError:
        print(f"❌ ERROR: I2C bus {I2C_BUS} not found")
        print("   Solutions:")
        print("   1. Enable I2C: sudo raspi-config → Interface Options → I2C → Enable")
        print("   2. Reboot: sudo reboot")
        return False

    except OSError as e:
        if "Remote I/O error" in str(e) or "[Errno 121]" in str(e):
            print(f"❌ ERROR: No device found at address 0x{BMP388_ADDRESS:02X}")
            print("\n🔧 Troubleshooting:")
            print("   1. Check if sensor is physically connected")
            print("   2. Verify wiring:")
            print("      VCC → 3.3V")
            print("      GND → Ground")
            print("      SDA → GPIO 2 (pin 3)")
            print("      SCL → GPIO 3 (pin 5)")
            print("   3. Scan I2C bus: sudo i2cdetect -y 1")
            print("   4. Try alternate address: 0x76")
            return False
        else:
            print(f"❌ ERROR: {e}")
            return False

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def scan_i2c_bus():
    """Scan I2C bus to find all connected devices"""
    print("\n🔍 Scanning I2C bus for devices...")
    print("=" * 50)

    try:
        import subprocess

        result = subprocess.run(
            ["i2cdetect", "-y", "1"], capture_output=True, text=True
        )
        print(result.stdout)
        print("\n💡 BMP388 should appear at address 77 (0x77) or 76 (0x76)")
    except FileNotFoundError:
        print("❌ i2cdetect command not found")
        print("   Install with: sudo apt-get install i2c-tools")
    except Exception as e:
        print(f"❌ Error scanning I2C bus: {e}")


if __name__ == "__main__":
    print("🍓 BMP388 Sensor Test - Raspberry Pi")
    print("=" * 50)
    print()

    success = test_bmp388()

    print("\n" + "=" * 50)

    if not success:
        scan_i2c_bus()
        print("\n❌ FAILED: BMP388 sensor test failed")
        print("   Review troubleshooting steps above")
        sys.exit(1)
    else:
        print("✅ PASSED: BMP388 sensor is ready to use")
        print("\n🚀 Start sensor server with:")
        print("   python3 pi_sensor_server.py")
        sys.exit(0)
