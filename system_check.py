"""
System Status Check - UIU MARINER ROV Control System
Verifies all components before launching the main application.
"""

import sys
import os
import json


def check_python_version():
    """Check Python version."""
    version = sys.version_info
    print(f"Python Version: {version.major}.{version.minor}.{version.micro}")
    if version.major == 3 and version.minor >= 8:
        print("  ✅ Python version OK")
        return True
    else:
        print("  ❌ Python 3.8+ required")
        return False


def check_virtual_env():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )
    if in_venv:
        print("  ✅ Running in virtual environment")
    else:
        print("  ⚠️ Not in virtual environment (recommended)")
    return True


def check_dependencies():
    """Check if all required packages are installed."""
    required = {
        "pymavlink": "MAVLink communication",
        "pygame": "Joystick input",
        "PyQt6": "GUI framework",
        "cv2": "OpenCV camera processing",
        "numpy": "Array operations",
        "serial": "Serial communication",
    }

    all_ok = True
    print("\nDependency Check:")
    for package, description in required.items():
        try:
            __import__(package)
            print(f"  ✅ {package:<15} - {description}")
        except ImportError:
            print(f"  ❌ {package:<15} - {description} (MISSING)")
            all_ok = False

    return all_ok


def check_config():
    """Check if config.json exists and is valid."""
    config_path = "config.json"

    if not os.path.exists(config_path):
        print(f"  ❌ config.json not found")
        return False

    try:
        with open(config_path, "r") as f:
            config = json.load(f)

        print("  ✅ config.json loaded")

        # Check important settings
        print(f"    MAVLink: {config.get('mavlink_connection', 'NOT SET')}")
        print(f"    Joystick: {config.get('joystick_target', 'auto-detect')}")
        print(f"    Mock Sensors: {config.get('sensors', {}).get('mock_mode', False)}")

        return True
    except Exception as e:
        print(f"  ❌ config.json error: {e}")
        return False


def check_joystick():
    """Check if joystick is detected."""
    try:
        import pygame

        pygame.init()
        pygame.joystick.init()

        count = pygame.joystick.get_count()

        if count == 0:
            print("  ⚠️ No joystick detected")
            print("    Connect your controller and run test_joystick.py")
            return True  # Don't fail - user can connect later

        print(f"  ✅ Found {count} joystick(s):")
        for i in range(count):
            js = pygame.joystick.Joystick(i)
            js.init()
            print(f"    {i}: {js.get_name()}")

        return True
    except Exception as e:
        print(f"  ❌ Joystick check failed: {e}")
        return False


def check_ui_file():
    """Check if main_window.ui exists."""
    ui_path = "src/ui/main_window.ui"

    if os.path.exists(ui_path):
        print(f"  ✅ UI file found: {ui_path}")
        return True
    else:
        print(f"  ⚠️ UI file not found: {ui_path}")
        print(f"    (This is okay if using Qt Designer externally)")
        return True  # Don't fail the check for this


def main():
    """Run all system checks."""
    print("=" * 70)
    print("UIU MARINER - SYSTEM STATUS CHECK")
    print("=" * 70)

    checks = {
        "Python Version": check_python_version(),
        "Virtual Environment": check_virtual_env(),
        "Dependencies": check_dependencies(),
        "Configuration": check_config(),
        "Joystick/Controller": check_joystick(),
        "UI Files": check_ui_file(),
    }

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    for name, status in checks.items():
        symbol = "✅" if status else "❌"
        print(f"{symbol} {name}")

    all_ok = all(checks.values())

    print("\n" + "=" * 70)

    if all_ok:
        print("✅ ALL SYSTEMS GO!")
        print("=" * 70)
        print("\nRun the application with:")
        print("  python launch_mariner.py")
    else:
        print("⚠️ SOME CHECKS FAILED")
        print("=" * 70)
        print("\nFix the issues above before launching the application.")
        print("\nFor help:")
        print("  - See README_COMPLETE.md")
        print("  - See QUICKSTART.md")
        print("  - Check VENV_GUIDE.md for virtual environment setup")

    print("\n")


if __name__ == "__main__":
    main()
