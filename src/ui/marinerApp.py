"""
UIU MARINER - Professional ROV Control System
Main application with camera feeds, object detection, sensor telemetry, and vehicle control
"""

import sys
import os
import json
import time
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QWidget
from PyQt6.QtCore import QTimer, Qt, pyqtSlot
from PyQt6.QtGui import QPixmap, QFont
from PyQt6 import uic

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from src.connections.mavlinkConnection import PixhawkConnection
from src.controllers.joystickController import JoystickController
from src.ui.cameraWorker import CameraWorker, DualCameraManager
from src.ui.sensorWorker import SensorTelemetryWorker, MockSensorWorker
from src.ui.cameraSelectionDialog import CameraSelectionDialog


class MarinerROVControl(QMainWindow):
    """
    Main application window for UIU MARINER ROV Control System.
    Integrates camera feeds, object detection, sensor telemetry, and vehicle control.
    """

    def __init__(self):
        super().__init__()

        # Load configuration
        self.config = self.load_config()

        # Initialize UI from .ui file
        self.init_ui()

        # Initialize components
        self.pixhawk = None
        self.joystick = None
        self.camera_manager = None
        self.sensor_worker = None

        # State variables
        self.armed = False
        self.current_mode = "MANUAL"
        self.thruster_values = [1500] * 8
        self.camera_detection_enabled = True
        self.active_camera = 0  # 0 or 1

        # Setup connections and start threads
        self.setup_connections()

        # Start components asynchronously for non-blocking startup
        print("[MARINER] 🚀 Starting components asynchronously...")

        # Start camera feeds (non-blocking)
        QTimer.singleShot(100, self.start_camera_feeds)

        # Start sensor telemetry (non-blocking with auto-fallback)
        QTimer.singleShot(200, self.start_sensor_telemetry)

        # Connect to Pixhawk (may take time)
        QTimer.singleShot(300, self.connect_pixhawk)

        # Initialize joystick
        QTimer.singleShot(400, self.init_joystick)

        # Start control loop
        self.control_timer = QTimer(self)
        self.control_timer.timeout.connect(self.control_loop)
        self.control_timer.start(250)  # 4 Hz - Further reduced for USB stability

        # UI update timer
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(1000)  # 1 Hz for UI updates - Reduced load

        print(
            "[MARINER] ✅ Application initialized - components starting in background"
        )

    def load_config(self):
        """Load configuration from JSON file."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        default_config = {
            "mavlink_connection": "tcp:raspberrypi.local:7000",
            "joystick_target": None,
            "camera": {
                "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
                "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
            },
            "sensors": {
                "host": "raspberrypi.local",
                "port": 5000,
                "protocol": "tcp",
                "mock_mode": False,
                "auto_connect": True,
            },
            "network": {
                "auto_detect": True,
                "pi_hostname": "raspberrypi.local",
                "fallback_ip": "192.168.0.100",
            },
            "thrusters": {
                "total_count": 8,
            },
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    loaded = json.load(f)
                    # Merge loaded config with defaults
                    merged = {**default_config, **loaded}
                    # Ensure nested dicts are also merged
                    for key in ["camera", "sensors", "network", "thrusters"]:
                        if key in loaded and key in default_config:
                            merged[key] = {**default_config[key], **loaded[key]}
                    return merged
        except Exception as e:
            print(f"[CONFIG] Error loading: {e}, using defaults")

        return default_config

    def init_ui(self):
        """Initialize UI from .ui file or create programmatically."""
        # Always use modern programmatic UI for best appearance
        print("[UI] 🎨 Creating modern UI...")
        self.ui_loaded = False
        self.create_ui_programmatically()

        # Set window properties
        self.setWindowTitle("UIU MARINER - ROV Control System")
        self.setMinimumSize(1024, 600)  # More flexible minimum size
        self.resize(1280, 720)  # Default size but user can resize

        # Find and store references to UI elements
        self.find_ui_elements()

    def create_ui_programmatically(self):
        """Create modern UI programmatically with sleek dark theme."""
        from PyQt6.QtWidgets import (
            QVBoxLayout,
            QHBoxLayout,
            QGroupBox,
            QFrame,
            QGridLayout,
        )

        # Modern color palette
        self.colors = {
            "bg_dark": "#0D1117",
            "bg_secondary": "#161B22",
            "bg_tertiary": "#21262D",
            "accent": "#FF8800",
            "accent_hover": "#FFA040",
            "success": "#00D084",
            "danger": "#FF4D4D",
            "warning": "#FFB800",
            "text_primary": "#E6EDF3",
            "text_secondary": "#8B949E",
            "border": "#30363D",
            "border_accent": "#FF8800",
        }

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Set main window style
        self.setStyleSheet(
            f"""
            QMainWindow {{
                background-color: {self.colors['bg_dark']};
            }}
            QWidget {{
                background-color: {self.colors['bg_dark']};
                color: {self.colors['text_primary']};
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QLabel {{
                color: {self.colors['text_primary']};
                background-color: transparent;
                font-size: 9pt;
            }}
            QGroupBox {{
                background-color: {self.colors['bg_secondary']};
                border: 1px solid {self.colors['border']};
                border-radius: 6px;
                padding: 10px;
                margin-top: 8px;
                font-weight: bold;
                font-size: 10pt;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 12px;
                color: {self.colors['accent']};
                background-color: {self.colors['bg_tertiary']};
                border: 1px solid {self.colors['border']};
                border-radius: 4px;
            }}
            QPushButton {{
                background-color: {self.colors['bg_tertiary']};
                border: 1px solid {self.colors['border']};
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 9pt;
                color: {self.colors['text_primary']};
                min-height: 30px;
            }}
            QPushButton:hover {{
                background-color: {self.colors['bg_secondary']};
                border-color: {self.colors['accent']};
            }}
            QPushButton:pressed {{
                background-color: {self.colors['bg_dark']};
            }}
            QPushButton#btnArm {{
                background-color: {self.colors['success']};
                color: #000;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton#btnArm:hover {{
                background-color: #00F0A0;
            }}
            QPushButton#btnEmergencyStop {{
                background-color: {self.colors['danger']};
                color: #FFF;
                font-size: 10pt;
                font-weight: bold;
            }}
            QPushButton#btnEmergencyStop:hover {{
                background-color: #FF6060;
            }}
            QPushButton#btnManualControl {{
                background-color: {self.colors['bg_tertiary']};
                color: {self.colors['accent']};
                font-size: 9pt;
                font-weight: bold;
                border: 2px solid {self.colors['accent']};
                border-radius: 6px;
            }}
            QPushButton#btnManualControl:hover {{
                background-color: {self.colors['accent']};
                color: #000;
            }}
            QPushButton#btnManualControl:pressed {{
                background-color: {self.colors['success']};
                color: #000;
                border-color: {self.colors['success']};
            }}
        """
        )

        # === TOP BAR ===
        top_bar = self.create_top_bar()
        main_layout.addWidget(top_bar)

        # === MAIN CONTENT === (Use scrollable area for better responsiveness)
        from PyQt6.QtWidgets import QScrollArea

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(
            f"""
            QScrollArea {{
                border: none;
                background-color: {self.colors['bg_dark']};
            }}
            QScrollBar:vertical {{
                background-color: {self.colors['bg_secondary']};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {self.colors['border']};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {self.colors['accent']};
            }}
        """
        )

        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(12, 12, 12, 12)
        content_layout.setSpacing(12)

        # Left column: Cameras
        camera_panel = self.create_camera_panel()
        content_layout.addWidget(camera_panel, 65)

        # Right column: Status & Controls
        right_panel = self.create_right_panel()
        content_layout.addWidget(right_panel, 35)

        scroll_area.setWidget(content)
        main_layout.addWidget(scroll_area)

        # === BOTTOM BAR ===
        bottom_bar = self.create_bottom_bar()
        main_layout.addWidget(bottom_bar)

    def create_top_bar(self):
        """Create modern top navigation bar."""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout

        top_bar = QFrame()
        top_bar.setFixedHeight(60)  # Reduced height
        top_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.colors['bg_secondary']};
                border-bottom: 2px solid {self.colors['border_accent']};
            }}
        """
        )

        layout = QHBoxLayout(top_bar)
        layout.setContentsMargins(16, 8, 16, 8)

        # Logo
        logo_label = QLabel()
        logo_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "public", "logo.png"
        )
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            # Scale logo to fit top bar (maintain aspect ratio)
            scaled_logo = logo_pixmap.scaled(
                40,
                40,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            logo_label.setPixmap(scaled_logo)
            logo_label.setStyleSheet("background-color: transparent;")
            layout.addWidget(logo_label)

        # Title
        title = QLabel("UIU MARINER")
        title.setStyleSheet(
            f"""
            font-size: 18pt;
            font-weight: bold;
            color: {self.colors['accent']};
            margin-left: 10px;
        """
        )
        layout.addWidget(title)

        layout.addStretch()

        # System time/status
        system_label = QLabel("ROV CONTROL SYSTEM")
        system_label.setStyleSheet(
            f"""
            font-size: 9pt;
            color: {self.colors['text_secondary']};
            font-weight: bold;
        """
        )
        layout.addWidget(system_label)

        return top_bar

    def create_camera_panel(self):
        """Create modern camera display panel."""
        from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QFrame

        panel = QFrame()
        panel.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.colors['bg_secondary']};
                border: 1px solid {self.colors['border']};
                border-radius: 12px;
            }}
        """
        )

        layout = QVBoxLayout(panel)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Main camera
        main_label = QLabel("PRIMARY CAMERA")
        main_label.setStyleSheet(
            f"""
            font-size: 9pt;
            font-weight: bold;
            color: {self.colors['accent']};
            padding: 6px;
        """
        )
        layout.addWidget(main_label)

        self.lblCameraMain = QLabel("🎥 Waiting for video feed...")
        self.lblCameraMain.setMinimumSize(640, 360)  # More flexible size
        self.lblCameraMain.setScaledContents(False)
        self.lblCameraMain.setStyleSheet(
            f"""
            background-color: #000;
            border: 2px solid {self.colors['border_accent']};
            border-radius: 6px;
            color: {self.colors['text_secondary']};
            font-size: 11pt;
        """
        )
        self.lblCameraMain.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lblCameraMain)

        # Secondary camera
        secondary_label = QLabel("SECONDARY CAMERA")
        secondary_label.setStyleSheet(
            f"""
            font-size: 8pt;
            font-weight: bold;
            color: {self.colors['text_secondary']};
            padding: 6px;
        """
        )
        layout.addWidget(secondary_label)

        self.lblCameraSmall = QLabel("🎥 Waiting for video feed...")
        self.lblCameraSmall.setMinimumSize(320, 180)  # More flexible size
        self.lblCameraSmall.setScaledContents(False)
        self.lblCameraSmall.setStyleSheet(
            f"""
            background-color: #000;
            border: 1px solid {self.colors['border']};
            border-radius: 5px;
            color: {self.colors['text_secondary']};
            font-size: 9pt;
        """
        )
        self.lblCameraSmall.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lblCameraSmall)

        return panel

    def create_right_panel(self):
        """Create modern right side panel with status and controls."""
        from PyQt6.QtWidgets import QVBoxLayout, QFrame

        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        # System Status
        status_panel = self.create_status_panel()
        layout.addWidget(status_panel)

        # Sensor Readings
        sensor_panel = self.create_sensor_panel()
        layout.addWidget(sensor_panel)

        # Control Buttons
        control_panel = self.create_control_panel()
        layout.addWidget(control_panel)

        layout.addStretch()

        return panel

    def create_status_panel(self):
        """Create system status panel."""
        from PyQt6.QtWidgets import QVBoxLayout, QGroupBox, QHBoxLayout

        group = QGroupBox("SYSTEM STATUS")
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # Pixhawk status
        pixhawk_row = QHBoxLayout()
        pixhawk_label = QLabel("Pixhawk:")
        pixhawk_label.setStyleSheet("font-weight: bold;")
        self.lblPixhawkStatus = QLabel("⚫ Disconnected")
        self.lblPixhawkStatus.setStyleSheet(f"color: {self.colors['text_secondary']};")
        pixhawk_row.addWidget(pixhawk_label)
        pixhawk_row.addWidget(self.lblPixhawkStatus)
        pixhawk_row.addStretch()
        layout.addLayout(pixhawk_row)

        # Joystick status
        joystick_row = QHBoxLayout()
        joystick_label = QLabel("Controller:")
        joystick_label.setStyleSheet("font-weight: bold;")
        self.lblJoystickStatus = QLabel("⚫ Disconnected")
        self.lblJoystickStatus.setStyleSheet(f"color: {self.colors['text_secondary']};")
        joystick_row.addWidget(joystick_label)
        joystick_row.addWidget(self.lblJoystickStatus)
        joystick_row.addStretch()
        layout.addLayout(joystick_row)

        # Mode status
        mode_row = QHBoxLayout()
        mode_label = QLabel("Mode:")
        mode_label.setStyleSheet("font-weight: bold;")
        self.lblModeStatus = QLabel("MANUAL")
        self.lblModeStatus.setStyleSheet(f"color: {self.colors['warning']};")
        mode_row.addWidget(mode_label)
        mode_row.addWidget(self.lblModeStatus)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        # Arm status
        arm_row = QHBoxLayout()
        arm_label = QLabel("Armed:")
        arm_label.setStyleSheet("font-weight: bold;")
        self.lblArmStatus = QLabel("⚫ NO")
        self.lblArmStatus.setStyleSheet(f"color: {self.colors['text_secondary']};")
        arm_row.addWidget(arm_label)
        arm_row.addWidget(self.lblArmStatus)
        arm_row.addStretch()
        layout.addLayout(arm_row)

        # Sensor status
        sensor_row = QHBoxLayout()
        sensor_label = QLabel("Sensors:")
        sensor_label.setStyleSheet("font-weight: bold;")
        self.lblSensorStatus = QLabel("⚫ Disconnected")
        self.lblSensorStatus.setStyleSheet(f"color: {self.colors['text_secondary']};")
        sensor_row.addWidget(sensor_label)
        sensor_row.addWidget(self.lblSensorStatus)
        sensor_row.addStretch()
        layout.addLayout(sensor_row)

        return group

    def create_sensor_panel(self):
        """Create sensor readings panel."""
        from PyQt6.QtWidgets import QVBoxLayout, QGroupBox, QGridLayout

        group = QGroupBox("SENSOR TELEMETRY")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 16, 10, 10)

        # Depth
        depth_label = QLabel("Depth")
        depth_label.setStyleSheet(
            f"font-size: 8pt; color: {self.colors['text_secondary']};"
        )
        self.lblDepth = QLabel("0.0 m")
        self.lblDepth.setStyleSheet(
            f"""
            font-size: 16pt;
            font-weight: bold;
            color: {self.colors['accent']};
            padding: 6px;
            background-color: {self.colors['bg_tertiary']};
            border-radius: 5px;
        """
        )
        self.lblDepth.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(depth_label, 0, 0)
        layout.addWidget(self.lblDepth, 1, 0, 1, 2)

        # Temperature
        temp_label = QLabel("Temperature")
        temp_label.setStyleSheet(
            f"font-size: 8pt; color: {self.colors['text_secondary']};"
        )
        self.lblTemperature = QLabel("0.0°C")
        self.lblTemperature.setStyleSheet(
            f"""
            font-size: 13pt;
            font-weight: bold;
            color: {self.colors['text_primary']};
            padding: 5px;
            background-color: {self.colors['bg_tertiary']};
            border-radius: 5px;
        """
        )
        self.lblTemperature.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(temp_label, 2, 0)
        layout.addWidget(self.lblTemperature, 3, 0)

        # Pressure
        pressure_label = QLabel("Pressure")
        pressure_label.setStyleSheet(
            f"font-size: 8pt; color: {self.colors['text_secondary']};"
        )
        self.lblPressure = QLabel("0.0 hPa")
        self.lblPressure.setStyleSheet(
            f"""
            font-size: 13pt;
            font-weight: bold;
            color: {self.colors['text_primary']};
            padding: 5px;
            background-color: {self.colors['bg_tertiary']};
            border-radius: 5px;
        """
        )
        self.lblPressure.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(pressure_label, 2, 1)
        layout.addWidget(self.lblPressure, 3, 1)

        return group

    def create_control_panel(self):
        """Create control buttons panel."""
        from PyQt6.QtWidgets import QVBoxLayout, QGroupBox

        group = QGroupBox("CONTROL PANEL")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 16, 10, 10)

        # ARM button
        self.btnArm = QPushButton("🔓 ARM THRUSTERS")
        self.btnArm.setObjectName("btnArm")
        self.btnArm.setMinimumHeight(45)
        self.btnArm.clicked.connect(self.toggle_arm)
        layout.addWidget(self.btnArm)

        # Emergency Stop
        self.btnEmergencyStop = QPushButton("⚠️ EMERGENCY STOP")
        self.btnEmergencyStop.setObjectName("btnEmergencyStop")
        self.btnEmergencyStop.setMinimumHeight(45)
        self.btnEmergencyStop.clicked.connect(self.emergency_stop)
        layout.addWidget(self.btnEmergencyStop)

        # Separator for manual controls
        manual_separator = QLabel("─" * 25)
        manual_separator.setStyleSheet(
            f"color: {self.colors['border']}; padding: 6px 0px; font-size: 8pt;"
        )
        manual_separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(manual_separator)

        # Manual Control Section Label
        manual_label = QLabel("🎮 MANUAL CONTROLS")
        manual_label.setStyleSheet(
            f"""
            font-size: 8pt;
            font-weight: bold;
            color: {self.colors['accent']};
            padding: 3px;
        """
        )
        manual_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(manual_label)

        # Manual control buttons in grid layout
        from PyQt6.QtWidgets import QGridLayout, QWidget

        manual_widget = QWidget()
        manual_layout = QGridLayout(manual_widget)
        manual_layout.setSpacing(8)
        manual_layout.setContentsMargins(0, 0, 0, 0)

        # Forward button (top center)
        self.btnForward = QPushButton("⬆️ FWD")
        self.btnForward.setObjectName("btnManualControl")
        self.btnForward.setMinimumHeight(40)
        self.btnForward.pressed.connect(lambda: self.send_manual_command("forward"))
        self.btnForward.released.connect(self.stop_manual_command)
        manual_layout.addWidget(self.btnForward, 0, 1)

        # Left button (middle left)
        self.btnLeft = QPushButton("⬅️ LEFT")
        self.btnLeft.setObjectName("btnManualControl")
        self.btnLeft.setMinimumHeight(40)
        self.btnLeft.pressed.connect(lambda: self.send_manual_command("left"))
        self.btnLeft.released.connect(self.stop_manual_command)
        manual_layout.addWidget(self.btnLeft, 1, 0)

        # Right button (middle right)
        self.btnRight = QPushButton("➡️ RIGHT")
        self.btnRight.setObjectName("btnManualControl")
        self.btnRight.setMinimumHeight(40)
        self.btnRight.pressed.connect(lambda: self.send_manual_command("right"))
        self.btnRight.released.connect(self.stop_manual_command)
        manual_layout.addWidget(self.btnRight, 1, 2)

        # Backward button (bottom center)
        self.btnBackward = QPushButton("⬇️ BWD")
        self.btnBackward.setObjectName("btnManualControl")
        self.btnBackward.setMinimumHeight(40)
        self.btnBackward.pressed.connect(lambda: self.send_manual_command("backward"))
        self.btnBackward.released.connect(self.stop_manual_command)
        manual_layout.addWidget(self.btnBackward, 2, 1)

        layout.addWidget(manual_widget)

        # Toggle Detection
        self.btnToggleDetection = QPushButton("👁️ Toggle Detection")
        self.btnToggleDetection.setMinimumHeight(36)
        self.btnToggleDetection.clicked.connect(self.toggle_detection)
        layout.addWidget(self.btnToggleDetection)

        # Separator
        separator = QLabel("─" * 25)
        separator.setStyleSheet(
            f"color: {self.colors['border']}; padding: 6px 0px; font-size: 8pt;"
        )
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(separator)

        # Camera Section Label
        camera_label = QLabel("📹 CAMERA CONTROLS")
        camera_label.setStyleSheet(
            f"""
            font-size: 8pt;
            font-weight: bold;
            color: {self.colors['accent']};
            padding: 3px;
        """
        )
        camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(camera_label)

        # Camera Configuration
        self.btnCameraConfig = QPushButton("📹 Camera Settings")
        self.btnCameraConfig.setObjectName("btnCameraConfig")
        self.btnCameraConfig.setMinimumHeight(42)
        self.btnCameraConfig.setStyleSheet(
            f"""
            QPushButton#btnCameraConfig {{
                background-color: {self.colors['accent']};
                color: white;
                font-size: 9pt;
                font-weight: bold;
                border: none;
                border-radius: 6px;
            }}
            QPushButton#btnCameraConfig:hover {{
                background-color: {self.colors['accent_hover']};
            }}
        """
        )
        self.btnCameraConfig.clicked.connect(self.open_camera_settings)
        layout.addWidget(self.btnCameraConfig)

        # Restart Camera Feeds
        self.btnRestartCameras = QPushButton("🔄 Restart Cameras")
        self.btnRestartCameras.setObjectName("btnRestartCameras")
        self.btnRestartCameras.setMinimumHeight(38)
        self.btnRestartCameras.setStyleSheet(
            f"""
            QPushButton#btnRestartCameras {{
                background-color: {self.colors['warning']};
                color: #000;
                font-size: 10pt;
                font-weight: bold;
                border: none;
                border-radius: 8px;
            }}
            QPushButton#btnRestartCameras:hover {{
                background-color: #FFD040;
            }}
        """
        )
        self.btnRestartCameras.clicked.connect(self.restart_camera_feeds)
        layout.addWidget(self.btnRestartCameras)

        return group

    def create_bottom_bar(self):
        """Create bottom status bar."""
        from PyQt6.QtWidgets import QFrame, QHBoxLayout

        bottom_bar = QFrame()
        bottom_bar.setFixedHeight(35)  # More compact
        bottom_bar.setStyleSheet(
            f"""
            QFrame {{
                background-color: {self.colors['bg_secondary']};
                border-top: 1px solid {self.colors['border']};
            }}
        """
        )

        layout = QHBoxLayout(bottom_bar)
        layout.setContentsMargins(16, 6, 16, 6)

        # Connection info (will be updated dynamically)
        self.conn_label = QLabel("● Network: Connecting...")
        self.conn_label.setStyleSheet(
            f"color: {self.colors['warning']}; font-size: 8pt;"
        )
        layout.addWidget(self.conn_label)

        layout.addStretch()

        # Version info
        version_label = QLabel("UIU MARINER v1.0 | ArduSub | 8-Thruster ROV")
        version_label.setStyleSheet(
            f"color: {self.colors['text_secondary']}; font-size: 8pt;"
        )
        layout.addWidget(version_label)

        return bottom_bar

        # Apply dark theme
        self.setStyleSheet(
            """
            QMainWindow, QWidget {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            QGroupBox {
                border: 2px solid #3f3f46;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FF8800;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #FF8800;
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #FF8800;
            }
            QLabel {
                color: white;
            }
        """
        )

    def find_ui_elements(self):
        """Find and store references to UI elements from loaded .ui file."""
        # Try to find elements from .ui file, fallback to programmatic ones
        # Only search if elements don't already exist (programmatic UI creates them directly)
        try:
            # Camera labels
            if not hasattr(self, "lblCameraSmall") or self.lblCameraSmall is None:
                self.lblCameraSmall = self.findChild(QLabel, "lblCameraSmall")
            if not hasattr(self, "lblCameraMain") or self.lblCameraMain is None:
                self.lblCameraMain = self.findChild(QLabel, "lblCameraMain")

            # Status labels
            if not hasattr(self, "lblPixhawkStatus") or self.lblPixhawkStatus is None:
                self.lblPixhawkStatus = self.findChild(QLabel, "lblPixhawkStatus")
            if not hasattr(self, "lblJoystickStatus") or self.lblJoystickStatus is None:
                self.lblJoystickStatus = self.findChild(QLabel, "lblJoystickStatus")
            if not hasattr(self, "lblModeStatus") or self.lblModeStatus is None:
                self.lblModeStatus = self.findChild(QLabel, "lblModeStatus")
            if not hasattr(self, "lblArmStatus") or self.lblArmStatus is None:
                self.lblArmStatus = self.findChild(QLabel, "lblArmStatus")

            # Sensor labels - DO NOT OVERWRITE if already created programmatically!
            if not hasattr(self, "lblDepth") or self.lblDepth is None:
                self.lblDepth = self.findChild(QLabel, "lblDepth")
            if not hasattr(self, "lblTemperature") or self.lblTemperature is None:
                self.lblTemperature = self.findChild(QLabel, "lblTemperature")
            if not hasattr(self, "lblPressure") or self.lblPressure is None:
                self.lblPressure = self.findChild(QLabel, "lblPressure")

            # Buttons
            if not hasattr(self, "btnArm") or self.btnArm is None:
                self.btnArm = self.findChild(QPushButton, "btnArm")
            if not hasattr(self, "btnEmergencyStop") or self.btnEmergencyStop is None:
                self.btnEmergencyStop = self.findChild(QPushButton, "btnEmergencyStop")
            if (
                not hasattr(self, "btnToggleDetection")
                or self.btnToggleDetection is None
            ):
                self.btnToggleDetection = self.findChild(
                    QPushButton, "btnToggleDetection"
                )

            print("[UI] ✅ Found UI elements")
        except Exception as e:
            print(f"[UI] Element finding error: {e}")

    def setup_connections(self):
        """Setup signal-slot connections for UI elements."""
        try:
            if hasattr(self, "btnArm") and self.btnArm:
                self.btnArm.clicked.connect(self.toggle_arm)

            if hasattr(self, "btnEmergencyStop") and self.btnEmergencyStop:
                self.btnEmergencyStop.clicked.connect(self.emergency_stop)

            if hasattr(self, "btnToggleDetection") and self.btnToggleDetection:
                self.btnToggleDetection.clicked.connect(self.toggle_detection)
        except:
            pass

    def start_camera_feeds(self):
        """Start dual camera feeds with object detection."""
        try:
            pipeline0 = self.config["camera"]["pipeline0"]
            pipeline1 = self.config["camera"]["pipeline1"]

            self.camera_manager = DualCameraManager(pipeline0, pipeline1)

            # Connect camera 0 to small display
            self.camera_manager.camera0.frame_ready.connect(self.update_camera_small)
            self.camera_manager.camera0.error_occurred.connect(self.handle_camera_error)

            # Connect camera 1 to main display
            self.camera_manager.camera1.frame_ready.connect(self.update_camera_main)
            self.camera_manager.camera1.error_occurred.connect(self.handle_camera_error)

            self.camera_manager.start_all()
            print("[CAMERAS] ✅ Dual camera feeds started")
        except Exception as e:
            print(f"[CAMERAS] ❌ Failed to start: {e}")

    def start_sensor_telemetry(self):
        """Start sensor telemetry worker."""
        try:
            # Always start in mock mode initially for faster startup
            # Will auto-switch to real mode if available
            if self.config["sensors"].get("mock_mode", False):
                self.sensor_worker = MockSensorWorker()
                print("[SENSORS] 🔧 Using mock data (testing mode)")
            else:
                # Try real sensor connection with auto-fallback to mock
                self.sensor_worker = SensorTelemetryWorker(
                    host=self.config["sensors"]["host"],
                    port=self.config["sensors"]["port"],
                    protocol=self.config["sensors"]["protocol"],
                    auto_mock_fallback=True,  # NEW: Auto-switch to mock on failure
                )

            # Connect signals with QueuedConnection to ensure thread safety
            self.sensor_worker.data_received.connect(
                self.update_sensor_display, Qt.ConnectionType.QueuedConnection
            )
            self.sensor_worker.connection_status.connect(
                self.handle_sensor_status, Qt.ConnectionType.QueuedConnection
            )

            # NEW: Connect error signal to trigger mock fallback
            if hasattr(self.sensor_worker, "error_occurred"):
                self.sensor_worker.error_occurred.connect(
                    self.handle_sensor_error, Qt.ConnectionType.QueuedConnection
                )

            # Start worker thread (non-blocking)
            self.sensor_worker.start()

            # Force GUI to remain responsive
            QApplication.processEvents()

        except Exception as e:
            print(f"[SENSORS] ❌ Failed to start: {e}")
            # Fallback to mock mode on any error
            self._fallback_to_mock_sensors()
            import traceback

            traceback.print_exc()

    def _fallback_to_mock_sensors(self):
        """Fallback to mock sensor mode."""
        print("[SENSORS] 🔄 Falling back to mock mode...")
        try:
            self.sensor_worker = MockSensorWorker()
            self.sensor_worker.data_received.connect(
                self.update_sensor_display, Qt.ConnectionType.QueuedConnection
            )
            self.sensor_worker.connection_status.connect(
                self.handle_sensor_status, Qt.ConnectionType.QueuedConnection
            )
            self.sensor_worker.start()
            print("[SENSORS] ✅ Mock mode active")
        except Exception as e:
            print(f"[SENSORS] ❌ Even mock mode failed: {e}")

    @pyqtSlot(str)
    def handle_sensor_error(self, error_msg):
        """Handle sensor connection errors."""
        print(f"[SENSORS] ⚠️ Error: {error_msg}")
        # Could trigger UI notification here

    def connect_pixhawk(self):
        """Connect to Pixhawk via MAVLink."""
        try:
            # Get auto-detect setting
            auto_detect = self.config.get("mavlink_auto_detect", False)

            self.pixhawk = PixhawkConnection(
                link=self.config["mavlink_connection"], auto_detect=auto_detect
            )

            if self.pixhawk.connect():
                print("[PIXHAWK] ✅ Connected")
                if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                    self.lblPixhawkStatus.setText(
                        f"Pixhawk: Connected ({self.pixhawk.link})"
                    )
                    self.lblPixhawkStatus.setStyleSheet("color: #00FF00;")
            else:
                print("[PIXHAWK] ❌ Connection failed")
                if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                    self.lblPixhawkStatus.setText("Pixhawk: Disconnected")
                    self.lblPixhawkStatus.setStyleSheet("color: #FF0000;")
        except Exception as e:
            print(f"[PIXHAWK] ❌ Error: {e}")
            if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                self.lblPixhawkStatus.setText("Pixhawk: Error")
                self.lblPixhawkStatus.setStyleSheet("color: #FF0000;")

    def init_joystick(self):
        """Initialize joystick controller."""
        try:
            target = self.config.get("joystick_target")
            self.joystick = JoystickController(target_name=target)

            if self.joystick.is_connected():
                print(f"[JOYSTICK] ✅ Connected: {self.joystick.joystick_name}")
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    self.lblJoystickStatus.setText(
                        f"Joystick: {self.joystick.joystick_name}"
                    )
                    self.lblJoystickStatus.setStyleSheet("color: #00FF00;")
            else:
                print(f"[JOYSTICK] ⚠️ No joystick connected")
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    self.lblJoystickStatus.setText("Joystick: Not Found")
                    self.lblJoystickStatus.setStyleSheet("color: #FF8800;")

        except Exception as e:
            print(f"[JOYSTICK] ❌ Error: {e}")
            if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                self.lblJoystickStatus.setText("Joystick: Error")
                self.lblJoystickStatus.setStyleSheet("color: #FF0000;")

    @pyqtSlot(QPixmap)
    def update_camera_small(self, pixmap):
        """Update small camera display."""
        if hasattr(self, "lblCameraSmall") and self.lblCameraSmall:
            self.lblCameraSmall.setPixmap(
                pixmap.scaled(
                    self.lblCameraSmall.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    @pyqtSlot(QPixmap)
    def update_camera_main(self, pixmap):
        """Update main camera display."""
        if hasattr(self, "lblCameraMain") and self.lblCameraMain:
            self.lblCameraMain.setPixmap(
                pixmap.scaled(
                    self.lblCameraMain.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )

    @pyqtSlot(dict)
    def update_sensor_display(self, data):
        """Update sensor display with new data."""
        try:
            if hasattr(self, "lblDepth") and self.lblDepth:
                self.lblDepth.setText(f"{data['depth']:.1f} m")

            if hasattr(self, "lblTemperature") and self.lblTemperature:
                self.lblTemperature.setText(f"{data['temperature']:.1f}°C")

            if hasattr(self, "lblPressure") and self.lblPressure:
                self.lblPressure.setText(f"{data['pressure']:.1f} hPa")

            # Force immediate UI update
            QApplication.processEvents()

        except Exception as e:
            print(f"[UI] ⚠️ Error updating sensor display: {e}")

    @pyqtSlot(bool)
    def handle_sensor_status(self, connected):
        """Handle sensor connection status changes."""
        status_text = "Sensors: Connected" if connected else "Sensors: Disconnected"
        status_color = "#00FF00" if connected else "#FF0000"
        print(f"[SENSORS] {'✅' if connected else '❌'} {status_text}")

        # Update UI label
        if hasattr(self, "lblSensorStatus") and self.lblSensorStatus:
            if connected:
                self.lblSensorStatus.setText("🟢 Connected")
                self.lblSensorStatus.setStyleSheet("color: #00FF00;")
            else:
                self.lblSensorStatus.setText("🔴 Disconnected")
                self.lblSensorStatus.setStyleSheet("color: #FF0000;")

        # Update bottom bar network status based on PIXHAWK connection
        # (Pi is connected if Pixhawk MAVProxy is accessible)
        if hasattr(self, "conn_label") and self.conn_label:
            # Check Pi connection via Pixhawk MAVProxy status
            pi_connected = (
                self.pixhawk and self.pixhawk.check_connection()
                if hasattr(self, "pixhawk")
                else False
            )

            if pi_connected:
                pi_host = self.config.get(
                    "mavlink_connection", "tcp:raspberrypi.local:7000"
                )
                # Extract hostname from connection string
                if ":" in pi_host:
                    pi_host = (
                        pi_host.split(":")[1]
                        if len(pi_host.split(":")) > 1
                        else "raspberrypi.local"
                    )
                self.conn_label.setText(f"● Network: {pi_host} (Connected)")
                self.conn_label.setStyleSheet(f"color: {self.colors['success']};")
            else:
                self.conn_label.setText("● Network: Disconnected")
                self.conn_label.setStyleSheet(f"color: {self.colors['danger']};")

    @pyqtSlot(str)
    def handle_camera_error(self, error_msg):
        """Handle camera errors."""
        print(f"[CAMERA ERROR] {error_msg}")

    def control_loop(self):
        """Main control loop - read joystick and send to Pixhawk."""
        try:
            if not self.joystick or not self.joystick.is_ready():
                return

            # Check connection status before sending commands
            try:
                if not self.pixhawk or not self.pixhawk.check_connection():
                    return
            except KeyboardInterrupt:
                raise  # Allow clean shutdown
            except Exception as e:
                print(f"[CONTROL] ⚠️ Connection check error: {e}")
                return

            # Read joystick
            joystick_state = self.joystick.read_joystick()

            # Convert to thruster channels
            channels = self.joystick.compute_thruster_channels(joystick_state)

            # Send to Pixhawk only if armed
            if self.armed:
                self.pixhawk.send_rc_channels_override(channels)
            else:
                # Debug: Show why commands aren't being sent
                if not hasattr(self, "_last_arm_warning"):
                    self._last_arm_warning = 0
                if time.time() - self._last_arm_warning > 5.0:
                    if any(
                        abs(ch - 1500) > 10 for ch in channels
                    ):  # Only warn if joystick moved
                        print(
                            "[CONTROL] ⚠️ Commands calculated but NOT sent - System not ARMED!"
                        )
                        print(
                            f"[CONTROL] 💡 Click 'ARM THRUSTERS' button to enable thruster control"
                        )
                        self._last_arm_warning = time.time()

            self.thruster_values = channels

        except KeyboardInterrupt:
            raise  # Allow clean shutdown
        except Exception as e:
            print(f"[CONTROL] ⚠️ Control loop error: {e}")

    def update_ui(self):
        """Periodic UI updates - display controller and thruster status."""
        try:
            # Update Pixhawk connection status
            if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                # Check if connection is still alive
                try:
                    if self.pixhawk:
                        is_connected = self.pixhawk.check_connection()
                    else:
                        is_connected = False
                except KeyboardInterrupt:
                    raise
                except Exception:
                    is_connected = False

                if is_connected:
                    self.lblPixhawkStatus.setText(
                        f"🟢 Pixhawk: Connected ({self.pixhawk.link})"
                    )
                    self.lblPixhawkStatus.setStyleSheet("color: #00FF00;")
                else:
                    self.lblPixhawkStatus.setText("🔴 Pixhawk: Disconnected")
                    self.lblPixhawkStatus.setStyleSheet("color: #FF0000;")

            # Update joystick connection status
            if self.joystick and self.joystick.is_connected():
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    ready = (
                        "✓ Ready" if self.joystick.is_ready() else "⏱ Calibrating..."
                    )
                    self.lblJoystickStatus.setText(
                        f"Joystick: {self.joystick.joystick_name} {ready}"
                    )
            else:
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    self.lblJoystickStatus.setText("🔴 Joystick: Disconnected")
                    self.lblJoystickStatus.setStyleSheet("color: #FF0000;")

            # Update thruster values if available
            if hasattr(self, "thruster_values") and self.thruster_values:
                # You can display thruster values here if you have labels for them
                # For now, just confirm they're being generated
                pass

        except Exception as e:
            print(f"[UI] ⚠️ Update error: {e}")

    def toggle_arm(self):
        """Toggle arm/disarm state."""
        if not self.pixhawk or not self.pixhawk.connected:
            print("[ARM] Cannot arm: Pixhawk not connected")
            return

        if self.armed:
            if self.pixhawk.disarm():
                self.armed = False
                if hasattr(self, "lblArmStatus"):
                    self.lblArmStatus.setText("Armed: NO")
                    self.lblArmStatus.setStyleSheet("color: #FF8800;")
                if hasattr(self, "btnArm"):
                    self.btnArm.setText("ARM THRUSTERS")
                print("[ARM] ⚠️ Disarmed")
        else:
            if self.pixhawk.arm():
                self.armed = True
                if hasattr(self, "lblArmStatus"):
                    self.lblArmStatus.setText("Armed: YES")
                    self.lblArmStatus.setStyleSheet(
                        "color: #00FF00; font-weight: bold;"
                    )
                if hasattr(self, "btnArm"):
                    self.btnArm.setText("DISARM THRUSTERS")
                print("[ARM] ✅ Armed - CAUTION!")

    def emergency_stop(self):
        """Emergency stop - disarm and neutral all thrusters."""
        print("[EMERGENCY] 🚨 EMERGENCY STOP ACTIVATED")

        if self.pixhawk and self.pixhawk.connected:
            # Send neutral commands
            neutral = [1500] * 8
            self.pixhawk.send_rc_channels_override(neutral)

            # Disarm
            if self.armed:
                self.pixhawk.disarm()
                self.armed = False
                if hasattr(self, "lblArmStatus"):
                    self.lblArmStatus.setText("Armed: NO")
                    self.lblArmStatus.setStyleSheet("color: #FF8800;")
                if hasattr(self, "btnArm"):
                    self.btnArm.setText("ARM THRUSTERS")

    def send_manual_command(self, direction):
        """Send manual thruster command when button pressed."""
        # Check if Pixhawk is connected and armed
        if not self.pixhawk or not self.pixhawk.connected:
            print(f"[MANUAL] ⚠️ Cannot send {direction} command: Pixhawk not connected")
            return

        if not self.armed:
            print(f"[MANUAL] ⚠️ Cannot send {direction} command: System not armed")
            return

        # Create neutral channels (1500 = neutral)
        channels = [1500] * 8

        # Set thrust based on direction (using moderate power: 1600 or 1400)
        # Channel mapping (typical for ROV):
        # 0-3: Forward/lateral thrusters
        # 4-7: Vertical thrusters

        if direction == "forward":
            # Forward thrusters (channels 0 and 1)
            channels[0] = 1600  # Forward power
            channels[1] = 1600
            print("[MANUAL] ⬆️ Forward command sent")

        elif direction == "backward":
            # Backward thrusters
            channels[0] = 1400  # Reverse power
            channels[1] = 1400
            print("[MANUAL] ⬇️ Backward command sent")

        elif direction == "left":
            # Left strafe (differential thrust)
            channels[2] = 1400  # Left power
            channels[3] = 1600
            print("[MANUAL] ⬅️ Left command sent")

        elif direction == "right":
            # Right strafe
            channels[2] = 1600  # Right power
            channels[3] = 1400
            print("[MANUAL] ➡️ Right command sent")

        # Send the command
        try:
            self.pixhawk.send_rc_channels_override(channels)
        except Exception as e:
            print(f"[MANUAL] ❌ Error sending command: {e}")

    def stop_manual_command(self):
        """Stop manual command when button released (send neutral)."""
        if not self.pixhawk or not self.pixhawk.connected or not self.armed:
            return

        # Send neutral commands to stop thrusters
        neutral = [1500] * 8
        try:
            self.pixhawk.send_rc_channels_override(neutral)
            print("[MANUAL] ⏹️ Manual command stopped (neutral)")
        except Exception as e:
            print(f"[MANUAL] ❌ Error stopping command: {e}")

    def toggle_detection(self):
        """Toggle object detection on all cameras."""
        self.camera_detection_enabled = not self.camera_detection_enabled

        if self.camera_manager:
            self.camera_manager.toggle_all_detection(self.camera_detection_enabled)

        status = "ON" if self.camera_detection_enabled else "OFF"
        print(f"[DETECTION] Object detection: {status}")

    def open_camera_settings(self):
        """Open camera configuration dialog."""
        dialog = CameraSelectionDialog(self.config, self)
        dialog.cameras_updated.connect(self.update_camera_config)
        dialog.exec()

    def update_camera_config(self, camera_config):
        """Update camera configuration."""
        # Update config
        if "camera" not in self.config:
            self.config["camera"] = {}

        self.config["camera"]["pipeline0"] = camera_config["pipeline0"]
        self.config["camera"]["pipeline1"] = camera_config["pipeline1"]

        # Save config to file
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        try:
            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            print("[CONFIG] ✅ Camera configuration saved")
        except Exception as e:
            print(f"[CONFIG] ❌ Failed to save: {e}")

    def restart_camera_feeds(self):
        """Restart camera feeds with new configuration."""
        print("[CAMERAS] Restarting camera feeds...")

        # Stop existing cameras
        if self.camera_manager:
            self.camera_manager.stop_all()
            self.camera_manager = None

        # Wait a moment
        import time

        time.sleep(0.5)

        # Start new cameras with updated config
        self.start_camera_feeds()

        print("[CAMERAS] ✅ Camera feeds restarted")

    def closeEvent(self, event):
        """Clean up on window close."""
        print("[MARINER] Shutting down...")

        # Stop timers
        self.control_timer.stop()
        self.ui_update_timer.stop()

        # Disarm if armed
        if self.armed and self.pixhawk:
            self.pixhawk.disarm()

        # Close all connections
        if self.camera_manager:
            self.camera_manager.stop_all()

        if self.sensor_worker:
            self.sensor_worker.stop()

        if self.pixhawk:
            self.pixhawk.close()

        if self.joystick:
            self.joystick.close()

        print("[MARINER] ✅ Shutdown complete")
        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("UIU MARINER ROV Control")
    app.setOrganizationName("UIU")

    # Create and show main window
    window = MarinerROVControl()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
