import sys
import time
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QGroupBox,
    QGridLayout,
)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QFont

# Import custom modules
import os
import json

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from connections.mavlinkConnection import PixhawkConnection
from controllers.joystickController import JoystickController


class ROVControlGUI(QMainWindow):
    """Main application window for ROV control."""

    def __init__(self, config_path="config.json"):
        super().__init__()

        # Load configuration
        self.config = self.load_config(config_path)

        # Initialize components
        self.pixhawk = None
        self.joystick = None
        self.armed = False
        self.current_mode = "MANUAL"
        self.thruster_values = [1500] * 8

        # Setup UI
        self.init_ui()

        # Connect to Pixhawk
        self.connect_pixhawk()

        # Initialize joystick
        self.init_joystick()

        # Start control loop
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.control_loop)
        self.timer.start(100)  # 10 Hz update rate

    def load_config(self, config_path):
        """Load configuration from JSON file."""
        default_config = {
            "mavlink_connection": "udp:192.168.0.104:14550",
            "joystick_target": "xbox",
            "update_rate_hz": 10,
            "enable_safety_checks": True,
        }

        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    print(f"[CONFIG] Loaded from {config_path}")
                    return {**default_config, **config}
        except Exception as e:
            print(f"[CONFIG] Error loading config: {e}")

        print("[CONFIG] Using default configuration")
        return default_config

    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle("UIU MARINER - ROV Control System")
        self.setGeometry(100, 100, 1200, 800)

        # Apply dark theme
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #181e1c;
            }
            QWidget {
                background-color: #181e1c;
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #2a2a2a;
                color: white;
                border: 1px solid #FF8800;
                border-radius: 5px;
                padding: 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a3a3a;
            }
            QPushButton:pressed {
                background-color: #FF8800;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
            QGroupBox {
                border: 1px solid #0D363E;
                border-radius: 5px;
                margin-top: 10px;
                padding: 15px;
                font-weight: bold;
                color: #FF8800;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """
        )

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title = QLabel("UIU MARINER - ROV Control System")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FF8800; margin: 10px;")
        main_layout.addWidget(title)

        # Top row: Control buttons + Status
        top_row = QHBoxLayout()
        top_row.addWidget(self.create_control_panel())
        top_row.addWidget(self.create_status_panel())
        main_layout.addLayout(top_row)

        # Bottom row: Thruster display + Joystick info
        bottom_row = QHBoxLayout()
        bottom_row.addWidget(self.create_thruster_panel())
        bottom_row.addWidget(self.create_joystick_panel())
        main_layout.addLayout(bottom_row)

        # Info bar
        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet(
            "background-color: #2a2a2a; padding: 5px; border-radius: 3px;"
        )
        main_layout.addWidget(self.info_label)

    def create_control_panel(self):
        """Create control button panel."""
        group = QGroupBox("Vehicle Control")
        layout = QVBoxLayout()

        # Mode selection
        mode_layout = QHBoxLayout()
        mode_label = QLabel("Flight Mode:")
        mode_label.setStyleSheet("font-weight: normal;")
        mode_layout.addWidget(mode_label)

        self.mode_manual_btn = QPushButton("MANUAL")
        self.mode_manual_btn.clicked.connect(lambda: self.set_mode("MANUAL"))
        mode_layout.addWidget(self.mode_manual_btn)

        self.mode_stabilize_btn = QPushButton("STABILIZE")
        self.mode_stabilize_btn.clicked.connect(lambda: self.set_mode("STABILIZE"))
        mode_layout.addWidget(self.mode_stabilize_btn)

        layout.addLayout(mode_layout)

        # Arm/Disarm
        arm_layout = QHBoxLayout()
        self.arm_btn = QPushButton("ARM THRUSTERS")
        self.arm_btn.setStyleSheet(
            "QPushButton { background-color: #006600; border-color: #00FF00; }"
        )
        self.arm_btn.clicked.connect(self.toggle_arm)
        arm_layout.addWidget(self.arm_btn)

        self.emergency_btn = QPushButton("EMERGENCY STOP")
        self.emergency_btn.setStyleSheet(
            "QPushButton { background-color: #660000; border-color: #FF0000; }"
        )
        self.emergency_btn.clicked.connect(self.emergency_stop)
        arm_layout.addWidget(self.emergency_btn)

        layout.addLayout(arm_layout)

        # Reconnect button
        self.reconnect_btn = QPushButton("Reconnect Pixhawk")
        self.reconnect_btn.clicked.connect(self.connect_pixhawk)
        layout.addWidget(self.reconnect_btn)

        group.setLayout(layout)
        return group

    def create_status_panel(self):
        """Create status display panel."""
        group = QGroupBox("Connection Status")
        layout = QVBoxLayout()

        self.pixhawk_status_label = QLabel("Pixhawk: Disconnected")
        self.pixhawk_status_label.setStyleSheet("color: #FF0000; font-weight: normal;")
        layout.addWidget(self.pixhawk_status_label)

        self.joystick_status_label = QLabel("Joystick: Not Connected")
        self.joystick_status_label.setStyleSheet("color: #FF0000; font-weight: normal;")
        layout.addWidget(self.joystick_status_label)

        self.mode_status_label = QLabel(f"Mode: {self.current_mode}")
        self.mode_status_label.setStyleSheet("color: #FFFFFF; font-weight: normal;")
        layout.addWidget(self.mode_status_label)

        self.arm_status_label = QLabel("Armed: NO")
        self.arm_status_label.setStyleSheet(
            "color: #FF8800; font-weight: normal; font-size: 16px;"
        )
        layout.addWidget(self.arm_status_label)

        group.setLayout(layout)
        return group

    def create_thruster_panel(self):
        """Create thruster value display panel."""
        group = QGroupBox("Thruster Values (PWM)")
        layout = QGridLayout()

        self.thruster_labels = []
        for i in range(8):
            label = QLabel(f"Ch{i+1}:")
            label.setStyleSheet("font-weight: normal;")
            value_label = QLabel("1500")
            value_label.setStyleSheet(
                "color: #FF8800; font-weight: bold; font-size: 14px;"
            )

            row = i // 4
            col = (i % 4) * 2
            layout.addWidget(label, row, col)
            layout.addWidget(value_label, row, col + 1)

            self.thruster_labels.append(value_label)

        group.setLayout(layout)
        return group

    def create_joystick_panel(self):
        """Create joystick info panel."""
        group = QGroupBox("Joystick Input")
        layout = QVBoxLayout()

        self.joystick_name_label = QLabel("Not Connected")
        self.joystick_name_label.setStyleSheet("font-weight: normal;")
        layout.addWidget(self.joystick_name_label)

        self.joystick_axes_label = QLabel("Axes: ---")
        self.joystick_axes_label.setStyleSheet("font-weight: normal; font-size: 10px;")
        layout.addWidget(self.joystick_axes_label)

        layout.addStretch()

        group.setLayout(layout)
        return group

    def connect_pixhawk(self):
        """Connect to Pixhawk via MAVLink."""
        self.info_label.setText("Connecting to Pixhawk...")
        self.pixhawk = PixhawkConnection(self.config["mavlink_connection"])

        if self.pixhawk.connect():
            self.pixhawk_status_label.setText(
                f"Pixhawk: Connected ({self.config['mavlink_connection']})"
            )
            self.pixhawk_status_label.setStyleSheet(
                "color: #00FF00; font-weight: normal;"
            )
            self.info_label.setText("Pixhawk connected successfully")
        else:
            self.pixhawk_status_label.setText("Pixhawk: Connection Failed")
            self.pixhawk_status_label.setStyleSheet(
                "color: #FF0000; font-weight: normal;"
            )
            self.info_label.setText("Failed to connect to Pixhawk")

    def init_joystick(self):
        """Initialize joystick controller."""
        try:
            target_name = self.config.get("joystick_target", None)
            self.joystick = JoystickController(target_name=target_name)

            if self.joystick.is_connected():
                self.joystick_status_label.setText(
                    f"Joystick: {self.joystick.joystick_name}"
                )
                self.joystick_status_label.setStyleSheet(
                    "color: #00FF00; font-weight: normal;"
                )
                self.joystick_name_label.setText(self.joystick.joystick_name)
                self.info_label.setText("Joystick connected")
            else:
                self.joystick_status_label.setText("Joystick: Not Found")
                self.joystick_status_label.setStyleSheet(
                    "color: #FF0000; font-weight: normal;"
                )
        except Exception as e:
            print(f"[ERROR] Joystick initialization failed: {e}")
            self.info_label.setText(f"Joystick error: {e}")

    def set_mode(self, mode):
        """Set flight mode."""
        if self.pixhawk and self.pixhawk.set_mode(mode):
            self.current_mode = mode
            self.mode_status_label.setText(f"Mode: {mode}")
            self.info_label.setText(f"Mode changed to {mode}")

    def toggle_arm(self):
        """Toggle arm/disarm state."""
        if not self.pixhawk or not self.pixhawk.connected:
            self.info_label.setText("Cannot arm: Pixhawk not connected")
            return

        if self.armed:
            if self.pixhawk.disarm():
                self.armed = False
                self.arm_status_label.setText("Armed: NO")
                self.arm_status_label.setStyleSheet(
                    "color: #FF8800; font-weight: normal; font-size: 16px;"
                )
                self.arm_btn.setText("ARM THRUSTERS")
                self.info_label.setText("Thrusters disarmed")
        else:
            if self.pixhawk.arm():
                self.armed = True
                self.arm_status_label.setText("Armed: YES")
                self.arm_status_label.setStyleSheet(
                    "color: #00FF00; font-weight: bold; font-size: 16px;"
                )
                self.arm_btn.setText("DISARM THRUSTERS")
                self.info_label.setText("Thrusters armed - CAUTION!")

    def emergency_stop(self):
        """Emergency stop - disarm and neutral all thrusters."""
        if self.pixhawk and self.pixhawk.connected:
            # Send neutral commands
            neutral = [1500] * 8
            self.pixhawk.send_rc_channels_override(neutral)

            # Disarm
            if self.armed:
                self.pixhawk.disarm()
                self.armed = False
                self.arm_status_label.setText("Armed: NO")
                self.arm_status_label.setStyleSheet(
                    "color: #FF8800; font-weight: normal; font-size: 16px;"
                )
                self.arm_btn.setText("ARM THRUSTERS")

            self.info_label.setText("EMERGENCY STOP ACTIVATED")

    def control_loop(self):
        """Main control loop - read joystick and send to Pixhawk."""
        if not self.joystick or not self.joystick.is_ready():
            return

        if not self.pixhawk or not self.pixhawk.connected:
            return

        # Read joystick
        joystick_state = self.joystick.read_joystick()

        # Convert to thruster channels
        channels = self.joystick.compute_thruster_channels(joystick_state)

        # Update display
        for i, value in enumerate(channels):
            self.thruster_labels[i].setText(str(value))

        # Update joystick axes display
        axes = joystick_state["axes"]
        axes_text = f"LX: {axes['left_x']:.2f} LY: {axes['left_y']:.2f} RX: {axes['right_x']:.2f} RY: {axes['right_y']:.2f}"
        self.joystick_axes_label.setText(axes_text)

        # Send to Pixhawk only if armed
        if self.armed:
            self.pixhawk.send_rc_channels_override(channels)

        # Store current values
        self.thruster_values = channels

    def closeEvent(self, event):
        """Clean up on window close."""
        # Stop timer
        self.timer.stop()

        # Disarm if armed
        if self.armed and self.pixhawk:
            self.pixhawk.disarm()

        # Close connections
        if self.pixhawk:
            self.pixhawk.close()

        if self.joystick:
            self.joystick.close()

        event.accept()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)

    # Set application info
    app.setApplicationName("UIU MARINER ROV Control")
    app.setOrganizationName("UIU")

    # Create and show main window
    window = ROVControlGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
