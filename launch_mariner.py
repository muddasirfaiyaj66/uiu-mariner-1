#!/usr/bin/env python3
"""
UIU MARINER - Launch Script
Professional ROV Ground Station Control System

Main entry point. Handles environment checks and application startup.
Supports both legacy Qt Widgets UI and modern QML interface.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


def check_venv() -> bool:
    """Check if running in virtual environment"""
    in_venv = hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )

    if not in_venv:
        logger.warning("Not running in virtual environment")
        return False

    logger.info("Virtual environment detected")
    return True


def check_dependencies() -> bool:
    """Check if required packages are installed"""
    required = {
        "PyQt6": "PyQt6",
        "pymavlink": "pymavlink",
        "pygame": "pygame",
        "cv2": "opencv-python",
        "numpy": "numpy",
    }

    missing = []

    for import_name, package_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package_name)

    if missing:
        logger.error(f"Missing dependencies: {', '.join(missing)}")
        return False

    logger.info("All dependencies installed")
    return True


def launch_qml_interface():
    """Launch the modern QML-based interface"""
    logger.info("Launching QML interface...")
    try:
        from src.views.qml_bridge_pyqt6 import main as qml_main
        return qml_main()
    except Exception as e:
        logger.error(f"Failed to launch QML interface: {e}", exc_info=True)
        return 1


def launch_widgets_interface():
    """Launch the legacy Qt Widgets interface"""
    logger.info("Launching Qt Widgets interface...")
    try:
        from src.views.mainWindow import MarinerROVControl
        from PyQt6.QtWidgets import QApplication

        # Create Qt application
        app = QApplication(sys.argv)

        # Create and show main window
        window = MarinerROVControl()
        window.show()

        logger.info("Application started successfully")
        return app.exec()
    except Exception as e:
        logger.error(f"Failed to launch Widgets interface: {e}", exc_info=True)
        return 1


def main():
    """Main application launcher"""
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser(
            description="UIU MARINER - ROV Ground Station Control System"
        )
        parser.add_argument(
            "--ui",
            choices=["qml", "widgets"],
            default="qml",
            help="Choose UI interface (default: qml)",
        )
        parser.add_argument(
            "--legacy",
            action="store_true",
            help="Launch legacy Qt Widgets interface (shortcut for --ui widgets)",
        )
        args = parser.parse_args()

        logger.info("=" * 60)
        logger.info("UIU MARINER - Ground Station Control System")
        logger.info("=" * 60)

        # Check dependencies
        if not check_dependencies():
            logger.error("Please run: pip install -r requirements.txt")
            sys.exit(1)

        # Set up path for imports
        project_root = Path(__file__).parent
        sys.path.insert(0, str(project_root))

        # Determine which UI to launch
        ui_mode = "widgets" if args.legacy else args.ui

        # Launch appropriate interface
        if ui_mode == "qml":
            logger.info("Interface Mode: Modern QML")
            exit_code = launch_qml_interface()
        else:
            logger.info("Interface Mode: Legacy Qt Widgets")
            exit_code = launch_widgets_interface()

        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
