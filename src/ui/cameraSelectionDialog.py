"""
Camera Selection Dialog
Allows users to select and configure camera sources for the ROV
"""

from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QGroupBox,
    QMessageBox,
    QLineEdit,
    QSpinBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
import subprocess
import json


class CameraSelectionDialog(QDialog):
    """Dialog for selecting camera sources."""

    cameras_updated = pyqtSignal(dict)  # Emits updated camera configuration

    def __init__(self, current_config, parent=None):
        super().__init__(parent)
        self.current_config = current_config
        self.available_cameras = []

        self.setWindowTitle("Camera Configuration")
        self.setMinimumWidth(600)
        self.init_ui()

    def init_ui(self):
        """Initialize the UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # Title
        title = QLabel("📹 Camera Configuration")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #FF8800;")
        layout.addWidget(title)

        # Detect cameras button
        detect_layout = QHBoxLayout()
        self.btnDetect = QPushButton("🔍 Detect Available Cameras")
        self.btnDetect.clicked.connect(self.detect_cameras)
        self.btnDetect.setStyleSheet(
            """
            QPushButton {
                background-color: #FF8800;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #FFA040;
            }
        """
        )
        detect_layout.addWidget(self.btnDetect)
        detect_layout.addStretch()
        layout.addLayout(detect_layout)

        # Status label
        self.lblStatus = QLabel(
            "Click 'Detect Available Cameras' to scan for cameras on Raspberry Pi"
        )
        self.lblStatus.setWordWrap(True)
        self.lblStatus.setStyleSheet("color: #8B949E; padding: 8px;")
        layout.addWidget(self.lblStatus)

        # Camera 0 Selection
        self.camera0_group = self.create_camera_group("Camera 0 (Primary)", 0)
        layout.addWidget(self.camera0_group)

        # Camera 1 Selection
        self.camera1_group = self.create_camera_group("Camera 1 (Secondary)", 1)
        layout.addWidget(self.camera1_group)

        # Manual Pipeline Entry
        manual_group = QGroupBox("Manual Pipeline Configuration (Advanced)")
        manual_layout = QVBoxLayout(manual_group)

        # Pipeline 0
        pipeline0_layout = QHBoxLayout()
        pipeline0_layout.addWidget(QLabel("Pipeline 0:"))
        self.txtPipeline0 = QLineEdit(
            self.current_config.get("camera", {}).get("pipeline0", "")
        )
        self.txtPipeline0.setPlaceholderText("GStreamer pipeline for camera 0")
        pipeline0_layout.addWidget(self.txtPipeline0)
        manual_layout.addLayout(pipeline0_layout)

        # Pipeline 1
        pipeline1_layout = QHBoxLayout()
        pipeline1_layout.addWidget(QLabel("Pipeline 1:"))
        self.txtPipeline1 = QLineEdit(
            self.current_config.get("camera", {}).get("pipeline1", "")
        )
        self.txtPipeline1.setPlaceholderText("GStreamer pipeline for camera 1")
        pipeline1_layout.addWidget(self.txtPipeline1)
        manual_layout.addLayout(pipeline1_layout)

        layout.addWidget(manual_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.btnCancel = QPushButton("Cancel")
        self.btnCancel.clicked.connect(self.reject)
        self.btnCancel.setStyleSheet(
            """
            QPushButton {
                background-color: #30363D;
                color: white;
                border: 1px solid #8B949E;
                border-radius: 6px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #21262D;
            }
        """
        )
        button_layout.addWidget(self.btnCancel)

        self.btnApply = QPushButton("Apply Configuration")
        self.btnApply.clicked.connect(self.apply_configuration)
        self.btnApply.setStyleSheet(
            """
            QPushButton {
                background-color: #00D084;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00F096;
            }
        """
        )
        button_layout.addWidget(self.btnApply)

        layout.addLayout(button_layout)

    def create_camera_group(self, title, camera_index):
        """Create a camera selection group."""
        group = QGroupBox(title)
        layout = QVBoxLayout(group)

        # Camera source selection
        source_layout = QHBoxLayout()
        source_layout.addWidget(QLabel("Source:"))

        source_combo = QComboBox()
        source_combo.addItem("Select camera...", None)
        source_combo.setMinimumWidth(300)
        setattr(self, f"cmbCamera{camera_index}", source_combo)
        source_layout.addWidget(source_combo)
        source_layout.addStretch()

        layout.addLayout(source_layout)

        # Port selection
        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel("UDP Port:"))

        port_spin = QSpinBox()
        port_spin.setRange(5000, 65535)
        port_spin.setValue(5000 + camera_index)
        setattr(self, f"spinPort{camera_index}", port_spin)
        port_layout.addWidget(port_spin)
        port_layout.addStretch()

        layout.addLayout(port_layout)

        # Generated pipeline preview
        pipeline_label = QLabel("Pipeline: Not configured")
        pipeline_label.setWordWrap(True)
        pipeline_label.setStyleSheet(
            "color: #8B949E; font-family: monospace; font-size: 9pt;"
        )
        setattr(self, f"lblPipeline{camera_index}", pipeline_label)
        layout.addWidget(pipeline_label)

        # Connect signal to update pipeline preview
        source_combo.currentIndexChanged.connect(
            lambda: self.update_pipeline_preview(camera_index)
        )
        port_spin.valueChanged.connect(
            lambda: self.update_pipeline_preview(camera_index)
        )

        return group

    def detect_cameras(self):
        """Detect cameras on Raspberry Pi."""
        self.lblStatus.setText("🔍 Scanning for cameras on Raspberry Pi...")
        self.btnDetect.setEnabled(False)

        try:
            # Get Pi IP from config
            pi_host = self.current_config.get("sensors", {}).get(
                "host", "raspberrypi.local"
            )

            # Try to SSH and run detection script
            ssh_command = [
                "ssh",
                f"pi@{pi_host}",
                "python3 /home/pi/mariner/detect_cameras.py",
            ]

            result = subprocess.run(
                ssh_command, capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                # Parse JSON output
                camera_data = json.loads(result.stdout)
                self.available_cameras = camera_data.get("cameras", [])

                if self.available_cameras:
                    self.populate_camera_lists()
                    self.lblStatus.setText(
                        f"✅ Found {len(self.available_cameras)} camera(s): "
                        f"{camera_data.get('pi_cameras', 0)} Pi Camera(s), "
                        f"{camera_data.get('usb_cameras', 0)} USB Camera(s)"
                    )
                    self.lblStatus.setStyleSheet("color: #00D084; padding: 8px;")
                else:
                    self.lblStatus.setText("❌ No cameras detected on Raspberry Pi")
                    self.lblStatus.setStyleSheet("color: #FF4D4D; padding: 8px;")
                    QMessageBox.warning(
                        self,
                        "No Cameras Found",
                        "No cameras were detected on the Raspberry Pi.\n\n"
                        "Please check:\n"
                        "1. Camera connections\n"
                        "2. Pi Camera is enabled in raspi-config\n"
                        "3. USB cameras are plugged in",
                    )
            else:
                raise Exception(f"SSH command failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            self.lblStatus.setText("❌ Connection timeout - cannot reach Raspberry Pi")
            self.lblStatus.setStyleSheet("color: #FF4D4D; padding: 8px;")
            QMessageBox.critical(
                self,
                "Connection Timeout",
                f"Cannot connect to Raspberry Pi at {pi_host}\n\n"
                "Please check:\n"
                "1. Network connection\n"
                "2. Pi is powered on\n"
                "3. SSH is enabled on Pi",
            )
        except Exception as e:
            self.lblStatus.setText(f"❌ Error: {str(e)}")
            self.lblStatus.setStyleSheet("color: #FF4D4D; padding: 8px;")
            QMessageBox.critical(
                self,
                "Detection Error",
                f"Failed to detect cameras:\n\n{str(e)}\n\n"
                "You can still manually enter camera pipelines below.",
            )
        finally:
            self.btnDetect.setEnabled(True)

    def populate_camera_lists(self):
        """Populate camera combo boxes with detected cameras."""
        for camera_index in [0, 1]:
            combo = getattr(self, f"cmbCamera{camera_index}")
            combo.clear()
            combo.addItem("Select camera...", None)

            for camera in self.available_cameras:
                display_name = (
                    f"{camera['name']} ({camera['type']}) - {camera['device']}"
                )
                combo.addItem(display_name, camera)

    def update_pipeline_preview(self, camera_index):
        """Update the pipeline preview for a camera."""
        combo = getattr(self, f"cmbCamera{camera_index}")
        port_spin = getattr(self, f"spinPort{camera_index}")
        pipeline_label = getattr(self, f"lblPipeline{camera_index}")

        camera_data = combo.currentData()

        if camera_data:
            port = port_spin.value()
            # Generate GStreamer pipeline based on camera type
            if camera_data["type"] == "pi_camera":
                # Pi Camera uses libcamera → H.264 streaming
                pipeline = (
                    f"udpsrc port={port} ! "
                    f"application/x-rtp,encoding-name=H264,payload={96 + camera_index} ! "
                    f"rtph264depay ! avdec_h264 ! videoconvert ! appsink"
                )
            else:  # USB camera
                # USB camera uses v4l2 → H.264 streaming
                pipeline = (
                    f"udpsrc port={port} ! "
                    f"application/x-rtp,encoding-name=H264,payload={96 + camera_index} ! "
                    f"rtph264depay ! avdec_h264 ! videoconvert ! appsink"
                )

            pipeline_label.setText(f"Pipeline: {pipeline}")
            pipeline_label.setStyleSheet(
                "color: #00D084; font-family: monospace; font-size: 9pt;"
            )
        else:
            pipeline_label.setText("Pipeline: Not configured")
            pipeline_label.setStyleSheet(
                "color: #8B949E; font-family: monospace; font-size: 9pt;"
            )

    def apply_configuration(self):
        """Apply the camera configuration."""
        # Check if at least one camera is configured
        cam0_data = self.cmbCamera0.currentData()
        cam1_data = self.cmbCamera1.currentData()

        # Generate pipelines
        pipeline0 = None
        pipeline1 = None

        if cam0_data:
            port = self.spinPort0.value()
            payload = 96
            pipeline0 = (
                f"udpsrc port={port} ! "
                f"application/x-rtp,encoding-name=H264,payload={payload} ! "
                f"rtph264depay ! avdec_h264 ! videoconvert ! appsink"
            )
        elif self.txtPipeline0.text().strip():
            pipeline0 = self.txtPipeline0.text().strip()

        if cam1_data:
            port = self.spinPort1.value()
            payload = 97
            pipeline1 = (
                f"udpsrc port={port} ! "
                f"application/x-rtp,encoding-name=H264,payload={payload} ! "
                f"rtph264depay ! avdec_h264 ! videoconvert ! appsink"
            )
        elif self.txtPipeline1.text().strip():
            pipeline1 = self.txtPipeline1.text().strip()

        if not pipeline0 and not pipeline1:
            QMessageBox.warning(
                self,
                "No Cameras Configured",
                "Please select at least one camera or enter a manual pipeline.",
            )
            return

        # Create camera configuration
        camera_config = {
            "pipeline0": pipeline0
            or self.current_config.get("camera", {}).get("pipeline0", ""),
            "pipeline1": pipeline1
            or self.current_config.get("camera", {}).get("pipeline1", ""),
            "camera0_data": cam0_data,
            "camera1_data": cam1_data,
        }

        # Emit signal with new configuration
        self.cameras_updated.emit(camera_config)

        # Show success message
        QMessageBox.information(
            self,
            "Configuration Applied",
            "Camera configuration has been updated.\n\n"
            "Please restart the camera feeds for changes to take effect.",
        )

        self.accept()
