import time
import numpy as np
import psutil
import socket
import serial
import cv2
import pygame
from PyQt6.QtWidgets import (
    QApplication,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QProgressBar,
    QSpacerItem,
    QSizePolicy,
    QSlider,
    QFrame,
    QGraphicsOpacityEffect,
)
from PyQt6.QtGui import (
    QPixmap,
    QImage,
    QPainter,
    QBrush,
    QColor,
    QPainterPath,
    QKeyEvent,
    QPixmap,
)
from PyQt6.QtCore import Qt, QRectF, QTimer, pyqtSignal
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import QThread
import cv2


class CameraWorker(QThread):
    frame_ready = pyqtSignal(object)  # Signal to send frame to GUI

    def __init__(self, pipeline, parent=None):
        super().__init__(parent)
        self.pipeline = pipeline
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.pipeline, cv2.CAP_GSTREAMER)

        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame)
        cap.release()

    def stop(self):
        self.running = False
        self.wait()


class ControlPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Initialize joystick first
        self.joystick = None
        self.joystick_name = "Not Connected"
        self.joystick_ready_time = time.time() + 1.5
        self.joystick_init()

        # Initialize UI
        self.init_ui()

        # Command management
        self.active_commands = []
        self.last_command_time = 0
        self.command_delay = 0.05  # 50ms delay for smoother control

        # Deadzone for analog sticks
        self.DEADZONE = 0.03

        # Setup joystick timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.read_joystick)
        self.timer.start(50)  # Read joystick every 50ms

        # MAVProxy connection
        self.mav_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Update this IP to match your Raspberry Pi
            self.mav_socket.connect(("raspberrypi.local", 7000))
            print("✅ Connected to MAVProxy server")
        except Exception as e:
            print(f"❌ Could not connect to MAVProxy server: {e}")
            print("Tip: Update the IP address in the code to match your Pi")

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        main_row = QHBoxLayout()

        frame_buttonLayout = QVBoxLayout()

        self.small_frame = QLabel()
        self.small_frame.setStyleSheet(
            " border: 1px solid #005767; border-radius: 20px; margin-bottom: 10px;"
        )
        self.small_frame.setFixedSize(384, 216)

        camerabtn_label = QLabel("SWITCH CAMERAS")
        camerabtn_label.setStyleSheet(
            """color: white; font-size: 12px; font-weight: bold; margin-top: 20px;"""
        )
        opacity_effect = QGraphicsOpacityEffect()
        camerabtn_label.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(0.6)

        camera01_btn = QPushButton("Camera 01")
        camera01_btn.setFixedSize(150, 50)
        camera01_btn.setStyleSheet(
            """
            background-color: transparent;
            color: white;
            font-size: 10px;
            padding: 5px;
            border: 1px solid #FF8800;
            border-radius: 5px;
            margin-top: 10px;
        """
        )

        camera02_btn = QPushButton("CAMERA ON")
        camera02_btn.setFixedSize(150, 50)
        camera02_btn.setStyleSheet(
            """
            background-color: transparent;
            color: white;
            font-size: 10px;
            padding: 5px;
            border: 1px solid #FF8800;
            border-radius: 5px;
            margin-top: 10px;
        """
        )

        frame_buttonLayout.addWidget(self.small_frame)
        frame_buttonLayout.addWidget(camerabtn_label)
        frame_buttonLayout.addWidget(camera01_btn)
        frame_buttonLayout.addWidget(camera02_btn)
        frame_buttonLayout.addStretch()

        # Main camera display
        self.main_camera = QLabel()
        self.main_camera.setFixedSize(960, 540)
        self.main_camera.setStyleSheet(
            " border: 1px solid #005767; border-radius: 20px;"
        )

        # Thrusters and Status
        thrusterstatus_layout = QVBoxLayout()

        status_container = QWidget()
        status_container.setStyleSheet(
            """
            background-color: #181818;
            border: 1px solid #0D363E;
            border-radius: 10px;
            padding: 10px;
        """
        )
        container_layout = QVBoxLayout()

        status_label = QLabel("Communication Status")
        status_label.setStyleSheet(
            """
            color: white;
            font-size: 8px;
            border: none;
        """
        )
        self.conn_label = QLabel("CONNECTING...")
        self.conn_label.setStyleSheet(
            """
            color: #FF8800;
            font-size: 20px;
            height: 30px;
            border: none;
        """
        )
        self.ip_label = QLabel("IP ADDRESS: Connecting...")
        self.ip_label.setStyleSheet(
            """
            color: white;
            font-size: 8px;
            border: none;
        """
        )
        container_layout.addWidget(status_label)
        container_layout.addWidget(self.conn_label)
        container_layout.addWidget(self.ip_label)
        status_container.setLayout(container_layout)
        status_container.setFixedSize(400, 130)

        # Control status widget
        control_status = QWidget()
        control_status.setStyleSheet(
            """
            background-color: #181818;
            border: 1px solid #0D363E;
            border-radius: 10px;
            padding: 10px;
        """
        )

        control_layout = QVBoxLayout()

        main_label = QLabel("DIRECTION")
        main_label.setStyleSheet(
            """
            color: white;
            font-size: 8px;
            border: none;
        """
        )

        self.dir_status = QLabel("NEUTRAL")
        self.dir_status.setStyleSheet(
            """
            color: #FF8800;
            font-size: 20px;
            border: none;
        """
        )

        up_label = QLabel("UP/DOWN")
        up_label.setStyleSheet(
            """
            color: white;
            font-size: 8px;
            border: none;
        """
        )

        # Thruster value labels (store as instance variables for updates)
        self.thruster_labels = {}

        for i in [2, 3, 6, 7]:
            layout = QHBoxLayout()
            label = QLabel(f"THRUSTER {i}")
            label.setStyleSheet("color: white; border: none;")
            value = QLabel("1500")
            value.setStyleSheet("color: #FF8800;")
            layout.addWidget(label)
            layout.addWidget(value)
            control_layout.addLayout(layout)
            self.thruster_labels[i] = value

        fwd_label = QLabel("FORWARD/BACKWARD")
        fwd_label.setStyleSheet("font-size: 8px; border: none;")
        control_layout.addWidget(fwd_label)

        for i in [1, 4, 5, 8]:
            layout = QHBoxLayout()
            label = QLabel(f"THRUSTER {i}")
            label.setStyleSheet("color: white; border: none;")
            value = QLabel("1500")
            value.setStyleSheet("color: #FF8800;")
            layout.addWidget(label)
            layout.addWidget(value)
            control_layout.addLayout(layout)
            self.thruster_labels[i] = value

        control_status.setLayout(control_layout)

        thrusterstatus_layout.addWidget(status_container)
        thrusterstatus_layout.addWidget(control_status)
        thrusterstatus_layout.addStretch()

        main_row.addLayout(frame_buttonLayout)
        main_row.addWidget(self.main_camera, alignment=Qt.AlignmentFlag.AlignTop)
        main_row.addLayout(thrusterstatus_layout)
        main_row.addStretch()

        # Second row (sensors, alarms, joystick info)
        second_row = QHBoxLayout()

        sensor_layout = QVBoxLayout()
        sensor_label = QLabel("SENSORS")
        sensor_label.setStyleSheet(
            """font-size: 12px; font-weight: bold; color: white; margin-bottom: 40px;"""
        )

        depth_layout = QHBoxLayout()
        depth_label = QLabel("DEPTH")
        self.depth_value = QLabel("0 m")
        self.depth_value.setStyleSheet(
            "border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;"
        )
        self.depth_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        depth_label.setStyleSheet("color: white; font-size: 8px;")
        depth_layout.addWidget(depth_label)
        depth_layout.addWidget(self.depth_value)

        temp_layout = QHBoxLayout()
        temp_label = QLabel("TEMPERATURE")
        self.temp_value = QLabel("0 °C")
        self.temp_value.setStyleSheet(
            "border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;"
        )
        self.temp_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        temp_layout.addWidget(temp_label)
        temp_layout.addWidget(self.temp_value)

        pressure_layout = QHBoxLayout()
        pressure_label = QLabel("PRESSURE")
        self.pressure_value = QLabel("0 Pa")
        self.pressure_value.setStyleSheet(
            "border: 1px solid #0D363E; border-radius: 5px; padding: 10px; color: #FF8800;"
        )
        self.pressure_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pressure_layout.addWidget(pressure_label)
        pressure_layout.addWidget(self.pressure_value)

        sensor_layout.addWidget(sensor_label)
        sensor_layout.addLayout(depth_layout)
        sensor_layout.addLayout(temp_layout)
        sensor_layout.addLayout(pressure_layout)
        sensor_layout.addStretch()

        # Leak and Emergency Alarm
        alarm_layout = QVBoxLayout()
        leak_label = QLabel("LEAK ALARM")
        leak_label.setStyleSheet(
            "color: #4F4F4F; background: #4F4F4F; font-size: 10px; border-radius: 50px; padding: 10px; color: white;"
        )
        leak_label.setFixedSize(100, 100)
        leak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        emergency_label = QPushButton("EMERGENCY")
        emergency_label.setStyleSheet(
            "border: 1px solid red; border-radius: 5px; padding: 10px; color: red; font-size: 10px; background-color: transparent;"
        )
        emergency_label.clicked.connect(self.emergency_stop)

        alarm_layout.addWidget(leak_label)
        alarm_layout.addWidget(emergency_label)
        alarm_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Joystick info
        joystick_layout = QVBoxLayout()
        image1_label = QLabel()
        pixmap1 = QPixmap(
            "Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA/assets/joystick.png"
        )
        if not pixmap1.isNull():
            image1_label.setPixmap(pixmap1)

        label1 = QLabel("MAIN JOYSTICK")
        label1.setStyleSheet("font-size: 10px;")
        self.conn_joystick1 = QLabel(self.joystick_name)
        self.conn_joystick1.setStyleSheet("font-size: 16px; color: #FF8800")

        joystick_layout.addWidget(image1_label)
        joystick_layout.addWidget(label1)
        joystick_layout.addWidget(self.conn_joystick1)

        second_row.addLayout(sensor_layout)
        second_row.addLayout(alarm_layout)
        second_row.addLayout(joystick_layout)

        # Add rows to main layout
        main_layout.addLayout(main_row)
        main_layout.addLayout(second_row)
        main_layout.addStretch()

    def start_video_threads(self):
        """Start camera video threads"""
        pipeline0 = (
            "udpsrc port=5000 ! application/x-rtp, encoding-name=H264, payload=96 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        pipeline1 = (
            "udpsrc port=5001 ! application/x-rtp, encoding-name=H264, payload=97 ! "
            "rtph264depay ! avdec_h264 ! videoconvert ! appsink"
        )

        self.cam0_worker = CameraWorker(pipeline0)
        self.cam1_worker = CameraWorker(pipeline1)

        self.cam0_worker.frame_ready.connect(
            lambda f: self.display_frame(f, self.small_frame)
        )
        self.cam1_worker.frame_ready.connect(
            lambda f: self.display_frame(f, self.main_camera)
        )

        self.cam0_worker.start()
        self.cam1_worker.start()

    def display_frame(self, frame, label):
        """Display video frame on label"""
        rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(
            rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
        )
        label.setPixmap(
            QPixmap.fromImage(qt_image).scaled(
                label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def send_command(self, command):
        """Send MAVLink command via socket"""
        try:
            self.mav_socket.sendall((command + "\n").encode())
            # print(f"Sent: {command}")  # Uncomment for debugging
        except Exception as e:
            print(f"❌ Failed to send command: {e}")

    def joystick_init(self):
        """Initialize joystick with auto-detection"""
        pygame.init()
        pygame.joystick.init()

        joystick_count = pygame.joystick.get_count()

        if joystick_count == 0:
            print("❌ No joystick detected")
            self.joystick_name = "Not Connected"
            return

        # Connect to first available joystick
        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.joystick_name = self.joystick.get_name()
        print(f"✅ Joystick Connected: {self.joystick_name}")

        # Update UI if it exists
        if hasattr(self, "conn_joystick1"):
            self.conn_joystick1.setText(self.joystick_name)

    def get_axis_value(self, axis_index, invert=False):
        """Get joystick axis value with deadzone"""
        if not self.joystick:
            return 0.0

        try:
            value = self.joystick.get_axis(axis_index)
            if invert:
                value = -value

            # Apply deadzone
            if abs(value) < self.DEADZONE:
                return 0.0
            return value
        except:
            return 0.0

    def axis_to_pwm(self, axis_value, reverse=False):
        """Convert axis value (-1.0 to 1.0) to PWM (1000-2000)"""
        if reverse:
            axis_value = -axis_value

        # Map -1.0...1.0 → 1000...2000
        pwm = 1500 + int(axis_value * 500)
        return max(1000, min(2000, pwm))

    def read_joystick(self):
        """Read joystick input and send RC commands"""
        if not self.joystick:
            return

        # Wait for calibration period
        if time.time() < self.joystick_ready_time:
            return

        pygame.event.pump()

        # Detect controller type for proper axis mapping
        controller_name = self.joystick_name.lower()

        if "switch" in controller_name:
            # Nintendo Switch Pro Controller mapping
            left_x = self.get_axis_value(0)
            left_y = self.get_axis_value(1, invert=True)
            right_x = self.get_axis_value(2)
            right_y = self.get_axis_value(3, invert=True)
        else:
            # Xbox 360 / Standard gamepad layout
            left_x = self.get_axis_value(0)
            left_y = self.get_axis_value(1, invert=True)
            right_x = self.get_axis_value(3)
            right_y = self.get_axis_value(4, invert=True)

        commands = []
        thruster_values = {}

        # Forward/Backward (Left Stick Y → Channels 1 and 8)
        if abs(left_y) > self.DEADZONE:
            value = self.axis_to_pwm(left_y)
            reverse_value = self.axis_to_pwm(-left_y)
            commands.append(f"rc 1 {value}")
            commands.append(f"rc 8 {reverse_value}")
            thruster_values[1] = value
            thruster_values[8] = reverse_value
            self.dir_status.setText("FORWARD" if left_y > 0 else "BACKWARD")
        else:
            commands.append("rc 1 1500")
            commands.append("rc 8 1500")
            thruster_values[1] = 1500
            thruster_values[8] = 1500

        # Left/Right Rotation (Left Stick X → Channels 2 and 5)
        if abs(left_x) > self.DEADZONE:
            value = self.axis_to_pwm(left_x)
            value2 = self.axis_to_pwm(-left_x)
            commands.append(f"rc 2 {value}")
            commands.append(f"rc 5 {value2}")
            thruster_values[2] = value
            thruster_values[5] = value2
            self.dir_status.setText("RIGHT" if left_x > 0 else "LEFT")
        else:
            commands.append("rc 2 1500")
            commands.append("rc 5 1500")
            thruster_values[2] = 1500
            thruster_values[5] = 1500

        # Up/Down (Right Stick Y → Channels 3, 4, 6, 7)
        if abs(right_y) > self.DEADZONE:
            value = self.axis_to_pwm(right_y)
            value2 = self.axis_to_pwm(-right_y)
            commands.append(f"rc 3 {value2}")
            commands.append(f"rc 4 {value2}")
            commands.append(f"rc 6 {value}")
            commands.append(f"rc 7 {value}")
            thruster_values[3] = value2
            thruster_values[4] = value2
            thruster_values[6] = value
            thruster_values[7] = value
            self.dir_status.setText("UP" if right_y > 0 else "DOWN")
        else:
            commands.append("rc 3 1500")
            commands.append("rc 4 1500")
            commands.append("rc 6 1500")
            commands.append("rc 7 1500")
            thruster_values[3] = 1500
            thruster_values[4] = 1500
            thruster_values[6] = 1500
            thruster_values[7] = 1500

        # If no movement, set to NEUTRAL
        if (
            abs(left_x) < self.DEADZONE
            and abs(left_y) < self.DEADZONE
            and abs(right_y) < self.DEADZONE
        ):
            self.dir_status.setText("NEUTRAL")

        # Update thruster UI labels
        for thruster_num, pwm_value in thruster_values.items():
            if thruster_num in self.thruster_labels:
                self.thruster_labels[thruster_num].setText(str(pwm_value))

        # Emergency stop button (e.g., Start button)
        try:
            if self.joystick.get_button(7):  # Start button
                self.emergency_stop()
                return
        except:
            pass

        # Throttle sending commands
        current_time = time.time()
        if current_time - self.last_command_time > self.command_delay:
            for command in commands:
                self.send_command(command)
            self.last_command_time = current_time

    def emergency_stop(self):
        """Emergency stop - set all thrusters to neutral"""
        print("⚠️ EMERGENCY STOP ACTIVATED")
        reset_commands = [
            "rc 1 1500",
            "rc 2 1500",
            "rc 3 1500",
            "rc 4 1500",
            "rc 5 1500",
            "rc 6 1500",
            "rc 7 1500",
            "rc 8 1500",
        ]
        for command in reset_commands:
            self.send_command(command)

        # Update UI
        self.dir_status.setText("EMERGENCY STOP")
        self.dir_status.setStyleSheet("color: #FF0000; font-size: 20px; border: none;")

        # Reset after 2 seconds
        QTimer.singleShot(
            2000,
            lambda: self.dir_status.setStyleSheet(
                "color: #FF8800; font-size: 20px; border: none;"
            ),
        )

        # Update all thruster displays
        for label in self.thruster_labels.values():
            label.setText("1500")

    def reset_commands(self):
        """Reset all RC commands to neutral"""
        reset_commands = [
            "rc 1 1500",
            "rc 2 1500",
            "rc 3 1500",
            "rc 4 1500",
            "rc 5 1500",
            "rc 6 1500",
            "rc 7 1500",
            "rc 8 1500",
        ]
        for command in reset_commands:
            self.send_command(command)
        self.active_commands.clear()

    def closeEvent(self, event):
        """Clean up on close"""
        self.reset_commands()
        if hasattr(self, "cam0_worker"):
            self.cam0_worker.stop()
        if hasattr(self, "cam1_worker"):
            self.cam1_worker.stop()
        if self.joystick:
            self.joystick.quit()
        pygame.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication([])
    app.setStyleSheet(
        """
        QWidget {
            background-color: #0A0A0A;
            color: white;
            font-family: 'Segoe UI', Arial, sans-serif;
        }
    """
    )

    window = ControlPage()
    window.showMaximized()
    window.start_video_threads()

    app.exec()
