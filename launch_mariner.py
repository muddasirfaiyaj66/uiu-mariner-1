"""
UIU MARINER - Launch Script
Quick launcher for the professional ROV control system
"""

import os
import sys
import subprocess


def check_venv():
    """Check if running in virtual environment."""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print("✅ Running in virtual environment")
        return True
    else:
        print("⚠️  Not running in virtual environment")
        venv_path = os.path.join(os.path.dirname(__file__), "venv")

        if os.path.exists(venv_path):
            print("💡 Virtual environment exists but not activated")
            print("\nActivate it with:")
            print("  PowerShell: .\\venv\\Scripts\\Activate.ps1")
            print("  CMD:        venv\\Scripts\\activate.bat")
            print("\nOr run setup script:")
            print("  setup.ps1   (PowerShell)")
            print("  setup.bat   (Command Prompt)")
            return False
        else:
            print("💡 No virtual environment found")
            print("\nCreate one by running:")
            print("  setup.ps1   (PowerShell)")
            print("  setup.bat   (Command Prompt)")
            return False


def check_dependencies():
    """Check if required packages are installed."""
    required = ["PyQt6", "pymavlink", "pygame", "cv2", "numpy"]
    missing = []

    for package in required:
        try:
            if package == "cv2":
                import cv2
            elif package == "numpy":
                import numpy
            elif package == "PyQt6":
                import PyQt6
            elif package == "pymavlink":
                import pymavlink
            elif package == "pygame":
                import pygame
        except ImportError:
            if package == "cv2":
                missing.append("opencv-python")
            else:
                missing.append(package)

    if missing:
        print("❌ Missing dependencies:")
        for pkg in missing:
            print(f"   - {pkg}")
        print("\n💡 Install them with:")
        if hasattr(sys, "real_prefix") or (
            hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
        ):
            print(f"   pip install {' '.join(missing)}")
        else:
            print("   First activate virtual environment, then:")
            print(f"   pip install {' '.join(missing)}")
        return False

    print("✅ All dependencies installed")
    return True


def main():
    """Launch the application."""
    print("=" * 60)
    print("UIU MARINER - ROV Control System")
    print("=" * 60)
    print()

    # Check virtual environment
    if not check_venv():
        print("\n⚠️  Recommended: Use virtual environment for cleaner setup")
        response = input("\nContinue anyway? (y/n): ").strip().lower()
        if response != "y":
            return
        print()

    # Check dependencies
    if not check_dependencies():
        print("\n⚠️ Please install missing dependencies first.")
        input("Press Enter to exit...")
        return

    print("\n🚀 Starting application...\n")

    # Launch main application
    app_path = os.path.join(os.path.dirname(__file__), "src", "ui", "marinerApp.py")

    try:
        # Run using current Python interpreter
        subprocess.run([sys.executable, app_path], check=True)
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()
