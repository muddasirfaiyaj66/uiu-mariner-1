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

# --- Import all required classes for logic connection ---
from ..computer_vision.camera_detector import CameraDetector
from .workers.sensorWorker import SensorTelemetryWorker
from ..services.mavlinkConnection import PixhawkConnection
from ..joystickController import JoystickController

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

# Delay heavy imports until needed in methods


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
        self.media_manager = None

        # State variables
        self.armed = False
        self.current_mode = "MANUAL"
        self.thruster_values = [1500] * 8
        self.camera_detection_enabled = True
        self.active_camera = 0
        self.recording_timer = None


        # Setup connections and start threads
        self.setup_connections()

        # Start components asynchronously for non-blocking startup
        print("[MARINER]  Starting components asynchronously...")

        # Start camera feeds (non-blocking)
        QTimer.singleShot(100, self.start_camera_feeds)

        # Start sensor telemetry (non-blocking with auto-fallback)
        QTimer.singleShot(200, self.start_sensor_telemetry)

        # Connect to Pixhawk (may take time)
        QTimer.singleShot(300, self.connect_pixhawk)

        # Initialize joystick
        QTimer.singleShot(400, self.init_joystick)

        # Delay import of MediaManager until here
        from .workers.mediaManager import MediaManager
        self.media_manager = MediaManager()

        # Start control loop
        self.control_timer = QTimer(self)
        self.control_timer.timeout.connect(self.control_loop)
        self.control_timer.start(500)

        # UI update timer
        self.ui_update_timer = QTimer(self)
        self.ui_update_timer.timeout.connect(self.update_ui)
        self.ui_update_timer.start(200)  # Faster UI updates for better responsiveness

        # Attitude update timer (faster updates for smooth compass)
        self.attitude_update_timer = QTimer(self)
        self.attitude_update_timer.timeout.connect(self.update_attitude_from_pixhawk)
        self.attitude_update_timer.start(100)  # Update every 100ms for smooth compass

        print(
            "[MARINER] [OK] Application initialized - components starting in background"
        )

    def load_config(self):
        """Load configuration from JSON file."""
        config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.json")
        default_config = {
            "mavlink_connection": "tcp:raspberrypi.local:7000",
            "joystick_target": None,
            "camera": {
                "stream_url0": "http://raspberrypi.local:8080/video_feed",
                "stream_url1": "http://raspberrypi.local:8081/video_feed",
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
        """Initialize UI from the new_ui_ui.py file."""
        print("[UI] Loading new UI design...")

        # Define color palette for status indicators (used in some methods)
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

        # Import and setup the new UI
        from .main_ui import Ui_MainWindow

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set window properties
        self.setWindowTitle("UIU MARINER - ROV Control System")

        print("[UI] [OK] New UI loaded successfully")

        # Find and store references to UI elements
        self.find_ui_elements()

        # Setup navigation between pages
        self.setup_navigation()

        # Initialize modern compass widget
        self.init_modern_compass()
        
        # Configure responsive design
        self.configure_responsive_layout()
        
        # Fix label text visibility - ensure HTML colors display properly
        # Use QTimer to delay this slightly so UI is fully rendered
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(100, self.fix_label_text_visibility)

        # --- SIDEBAR TOGGLE FUNCTIONALITY ---
        # Connect sidebar toggle button to show/hide sidebar
        if hasattr(self.ui, 'btnToggleSidebar') and hasattr(self.ui, 'side_frame'):
            self.ui.btnToggleSidebar.clicked.connect(self.toggle_sidebar)
        
        # Connect hamburger menu button
        if hasattr(self.ui, 'btnMenuToggle') and hasattr(self.ui, 'sideBar'):
            self.ui.btnMenuToggle.clicked.connect(self.toggle_sidebar)
        
        # Setup time display update timer
        if hasattr(self.ui, 'lblTime'):
            from PyQt6.QtCore import QTimer
            self.time_timer = QTimer()
            self.time_timer.timeout.connect(self.update_time_display)
            self.time_timer.start(1000)  # Update every second
            self.update_time_display()  # Initial update

        # --- LOGO LOAD PATCH ---
        # Load logo from public/logo.png
        import os
        from PyQt6.QtGui import QPixmap
        logo_paths = [
            os.path.join(os.path.dirname(__file__), '../../public/logo.png'),
            os.path.join(os.path.dirname(__file__), '../../media/images/logo.png'),
        ]
        logo_loaded = False
        for logo_path in logo_paths:
            if os.path.exists(logo_path):
                if hasattr(self.ui, 'lblLogoIcon'):
                    pixmap = QPixmap(logo_path)
                    if not pixmap.isNull():
                        self.ui.lblLogoIcon.setPixmap(pixmap)
                        self.ui.lblLogoIcon.setScaledContents(True)
                        logo_loaded = True
                        print(f"[UI] Logo loaded from: {logo_path}")
                        break
        if not logo_loaded:
            print("[UI] Warning: Logo file not found. Please ensure public/logo.png exists.")

        # --- FLOATING SIDEBAR TOGGLE BUTTON ---
        # Create a floating button that is always visible when sidebar is hidden
        self.floatingSidebarButton = QPushButton("☰", self)
        self.floatingSidebarButton.setObjectName("floatingSidebarButton")
        self.floatingSidebarButton.setFixedSize(36, 36)
        self.floatingSidebarButton.setStyleSheet("""
            QPushButton#floatingSidebarButton {
                background-color: #222;
                color: #ea8a35;
                border: 2px solid #ea8a35;
                border-radius: 8px;
                font-size: 18pt;
                font-weight: bold;
                padding: 0px;
                z-index: 1000;
            }
            QPushButton#floatingSidebarButton:hover {
                background-color: #333;
            }
        """)
        self.floatingSidebarButton.move(8, 60)  # Left edge, below top bar
        self.floatingSidebarButton.clicked.connect(self.toggle_sidebar)
        self.floatingSidebarButton.hide()  # Start hidden (sidebar visible by default)

        # Ensure floating button stays on top and in position on resize
        self.resizeEvent = self._wrap_resize_event(self.resizeEvent)

    def _wrap_resize_event(self, original_resize_event):
        def new_resize_event(event):
            # Place the floating button at the left edge, below top bar
            self.floatingSidebarButton.move(8, 60)
            self.floatingSidebarButton.raise_()
            original_resize_event(event)
        return new_resize_event
    def toggle_sidebar(self):
        """Show/hide the sidebar (sideBar) when the toggle button is pressed."""
        if hasattr(self.ui, 'sideBar'):
            is_visible = self.ui.sideBar.isVisible()
            self.ui.sideBar.setVisible(not is_visible)
            # Optionally, adjust main content margins if needed
            if hasattr(self.ui, 'mainContent'):
                self.ui.mainContent.setContentsMargins(0, 0, 0, 0)
            # Show floating button only when sidebar is hidden
            if not is_visible:
                if hasattr(self, 'floatingSidebarButton'):
                    self.floatingSidebarButton.hide()
            else:
                if hasattr(self, 'floatingSidebarButton'):
                    self.floatingSidebarButton.show()


    def find_ui_elements(self):
        """Map new UI elements to expected variable names and configure responsive behavior."""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QSizePolicy
        
        # No individual sensor value labels exist in the new UI, so skip this block.
        

        try:
            # Camera labels - map from new UI to old variable names
            if hasattr(self.ui, 'lblMainCameraFeed'):
                self.lblCameraMain = self.ui.lblMainCameraFeed
            elif hasattr(self.ui, 'lblCam1Feed'):
                self.lblCameraMain = self.ui.lblCam1Feed
            else:
                self.lblCameraMain = None
                print("[UI] Warning: Main camera feed label not found in UI")
            
            # Secondary cameras
            if hasattr(self.ui, 'lblBottomCameraFeed'):
                self.lblCameraSmall = self.ui.lblBottomCameraFeed
            elif hasattr(self.ui, 'lblCam2Feed'):
                self.lblCameraSmall = self.ui.lblCam2Feed
            else:
                self.lblCameraSmall = None
                print("[UI] Warning: Secondary camera feed label not found in UI")
            
            # Gripper camera (third camera)
            if hasattr(self.ui, 'lblGripperCameraFeed'):
                self.lblCameraGripper = self.ui.lblGripperCameraFeed
            else:
                self.lblCameraGripper = None
            
            # Ensure camera labels expand responsively and scale contents
            from PyQt6.QtWidgets import QSizePolicy
            if self.lblCameraMain:
                self.lblCameraMain.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.lblCameraMain.setScaledContents(True)
                self.lblCameraMain.setMinimumSize(320, 180)  # Minimum for smaller screens
                self.lblCameraMain.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            if self.lblCameraSmall:
                self.lblCameraSmall.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.lblCameraSmall.setScaledContents(True)
                self.lblCameraSmall.setMinimumSize(240, 135)  # Minimum for smaller screens
                self.lblCameraSmall.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Camera status labels
            if hasattr(self.ui, 'lblCameraMainStatus'):
                self.lblCameraMainStatus = self.ui.lblCameraMainStatus
            else:
                self.lblCameraMainStatus = None
            
            if hasattr(self.ui, 'lblCameraSmallStatus'):
                self.lblCameraSmallStatus = self.ui.lblCameraSmallStatus
            else:
                self.lblCameraSmallStatus = None



            # Buttons - map from new UI
            self.btnArm = self.ui.btnArmConnect  # ARM/CONNECT button
            self.btnEmergencyStop = self.ui.btnEmergencyStop

            # Media buttons
            self.btnCaptureImage = self.ui.btnCapture
            self.btnStartRecording = self.ui.btnRecord

            # Create placeholder for detection toggle (not in new UI, will add to settings)
            self.btnToggleDetection = None

            # Connection status label
            self.conn_label = self.ui.lblConnectionStatus

            # Attitude/Compass elements
            self.lblCompass = self.ui.lblCompass
            self.lblHeadingDisplay = self.ui.lblHeadingDisplay
            self.lblPitchValue = self.ui.lblPitchValue
            self.lblRollValue = self.ui.lblRollValue

            # Additional sensor depth label (there's also lblDepthLabel)
            self.lblDepthLabel = self.ui.lblDepthLabel

            # Camera status labels (lblCam1 for main camera, lblCam2 for secondary)
            self.lblCam1Status = self.ui.lblCam1
            self.lblCam2Status = self.ui.lblCam2

            print("[UI] [OK] Mapped new UI elements to expected variable names")
        except Exception as e:
            print(f"[UI] Element mapping error: {e}")
            import traceback

            traceback.print_exc()

    def setup_navigation(self):
        """Setup navigation between different pages in the stacked widget."""
        try:
            # Connect sidebar buttons to switch pages
            # Connect navigation buttons
            if hasattr(self.ui, 'btnMainControl'):
                self.ui.btnMainControl.clicked.connect(lambda: self.switch_page(0))
            if hasattr(self.ui, 'btnGallery'):
                self.ui.btnGallery.clicked.connect(lambda: self.switch_page(1))
            if hasattr(self.ui, 'btnMissionLogs'):
                self.ui.btnMissionLogs.clicked.connect(lambda: self.switch_page(2))
            if hasattr(self.ui, 'btnSystemStatus'):
                self.ui.btnSystemStatus.clicked.connect(lambda: self.switch_page(3))
            if hasattr(self.ui, 'btnSettings'):
                self.ui.btnSettings.clicked.connect(lambda: self.switch_page(4))

            # Set Main Control as default page
            self.ui.contentStack.setCurrentIndex(0)
            if hasattr(self.ui, 'btnMainControl'):
                self.ui.btnMainControl.setChecked(True)

            # Setup Mission Logs functionality
            self.setup_mission_logs()

            print("[UI] [OK] Navigation setup complete")
        except Exception as e:
            print(f"[UI] Navigation setup error: {e}")

    def init_modern_compass(self):
        """Initialize the modern compass widget to replace the placeholder."""
        try:
            from .workers.modernCompass import ModernCompass

            # Create modern compass widget
            self.compass_widget = ModernCompass()
            self.compass_widget.setMinimumSize(
                150, 150
            )  # Increased for better visibility
            self.compass_widget.setMaximumSize(
                200, 200
            )  # Increased for better visibility

            # Replace the lblCompass placeholder with the actual compass widget
            if hasattr(self, "lblCompass") and self.lblCompass:
                # Get the parent layout
                parent_layout = self.lblCompass.parent().layout()
                if parent_layout:
                    # Find the index of lblCompass in the layout
                    for i in range(parent_layout.count()):
                        if parent_layout.itemAt(i).widget() == self.lblCompass:
                            # Hide the placeholder
                            self.lblCompass.hide()
                            # Insert the compass widget at the same position
                            parent_layout.insertWidget(i, self.compass_widget)
                            break

            # Initialize attitude data
            self.current_heading = 0.0
            self.current_pitch = 0.0
            self.current_roll = 0.0

            print("[COMPASS] [OK] Modern compass widget initialized")
        except Exception as e:
            print(f"[COMPASS] [ERR] Failed to initialize: {e}")
            import traceback

            traceback.print_exc()

    def configure_responsive_layout(self):
        """Configure UI for responsive design - ensure elements scale properly on window resize."""
        try:
            from PyQt6.QtWidgets import QSizePolicy
            
            # Ensure main window can be resized
            self.setMinimumSize(800, 600)
            
            # Make sidebar responsive (if it exists)
            if hasattr(self.ui, 'side_frame') and self.ui.side_frame:
                self.ui.side_frame.setMinimumWidth(180)
                self.ui.side_frame.setMaximumWidth(280)
            
            # Configure main content area to be responsive
            if hasattr(self.ui, 'main_frame') and self.ui.main_frame:
                self.ui.main_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Make camera frames responsive
            if hasattr(self.ui, 'main_cam_frame') and self.ui.main_cam_frame:
                self.ui.main_cam_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            if hasattr(self.ui, 'cam2_frame') and self.ui.cam2_frame:
                self.ui.cam2_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Configure stacked widget for responsive behavior
            if hasattr(self.ui, 'contentStack') and self.ui.contentStack:
                self.ui.contentStack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            
            # Make top bar responsive
            if hasattr(self.ui, 'top_bar_frame') and self.ui.top_bar_frame:
                self.ui.top_bar_frame.setMaximumHeight(80)
            
            # Fix bottom panel layout - set stretch factors for proper distribution
            if hasattr(self.ui, 'horizontalLayout_4'):
                layout = self.ui.horizontalLayout_4
                # Set proper stretch factors for bottom panels
                # Attitude Indicator: 1, Sensor Data: 3, System Control: 1
                # This ensures Sensor Data gets more space as it's the most important panel
                if layout.count() > 0:
                    layout.setStretch(0, 1)  # Attitude panel - narrower
                if layout.count() > 1:
                    layout.setStretch(1, 3)  # Sensor Data panel - wider, more important
                if layout.count() > 2:
                    layout.setStretch(2, 1)  # System Control panel - medium width
            
            # Fix camera layout stretch factors - ensure proper ratio
            if hasattr(self.ui, 'horizontalLayout_3'):
                layout = self.ui.horizontalLayout_3
                # Camera 1 should be larger (stretch 2), Camera 2 smaller (stretch 1)
                if layout.count() > 0:
                    layout.setStretch(0, 2)  # Main camera
                if layout.count() > 1:
                    layout.setStretch(1, 1)  # Secondary camera
            
            # Make attitude frame more flexible (remove max width restriction)
            if hasattr(self.ui, 'attitude_frame') and self.ui.attitude_frame:
                # Allow it to grow but keep reasonable limits
                self.ui.attitude_frame.setMaximumWidth(16777215)  # Remove max width limit
                self.ui.attitude_frame.setMinimumWidth(200)
                self.ui.attitude_frame.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
            
            # Make sensor tab widget responsive
            if hasattr(self.ui, 'tabWidget') and self.ui.tabWidget:
                self.ui.tabWidget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.ui.tabWidget.setMinimumWidth(300)
            
            # Make control frame responsive if it exists
            if hasattr(self.ui, 'control_frame') and self.ui.control_frame:
                self.ui.control_frame.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
                self.ui.control_frame.setMinimumWidth(200)
            
            # Ensure main dashboard layout uses stretch properly
            if hasattr(self.ui, 'verticalLayout_6'):
                layout = self.ui.verticalLayout_6
                # Camera section (index 0) should take more vertical space
                if layout.count() > 0:
                    layout.setStretch(0, 2)  # Top section (cameras)
                # Bottom panels (index 1) should take less vertical space
                if layout.count() > 1:
                    layout.setStretch(1, 1)  # Bottom section (panels)
            
            print("[UI] [OK] Responsive layout configured with proper stretch factors")
        except Exception as e:
            print(f"[UI] [ERR] Failed to configure responsive layout: {e}")
            import traceback
            traceback.print_exc()

    def fix_label_text_visibility(self):
        """Fix text visibility issues in status frame labels by ensuring HTML colors render."""
        try:
            from PyQt6.QtCore import Qt
            from PyQt6.QtWidgets import QApplication
            import re
            
            # No status label lists exist in the new UI, so skip this block.
            pass
            # No label updates needed for new UI
            QApplication.processEvents()
            print("[UI] [OK] Label text visibility fixed - HTML colors should now display")
        except Exception as e:
            print(f"[UI] [ERR] Failed to fix label visibility: {e}")
            import traceback
            traceback.print_exc()

    def switch_page(self, index):
        """Switch to a different page in the stacked widget."""
        try:
            self.ui.contentStack.setCurrentIndex(index)

            # Load gallery when switching to gallery page
            if index == 1:  # Gallery page
                self.load_gallery()
            elif index == 2:  # Mission Logs page
                self.load_mission_logs()

            # Update button checked states
            if hasattr(self.ui, 'btnMainControl'):
                self.ui.btnMainControl.setChecked(index == 0)
            if hasattr(self.ui, 'btnGallery'):
                self.ui.btnGallery.setChecked(index == 1)
            if hasattr(self.ui, 'btnMissionLogs'):
                self.ui.btnMissionLogs.setChecked(index == 2)
            if hasattr(self.ui, 'btnSystemStatus'):
                self.ui.btnSystemStatus.setChecked(index == 3)
            if hasattr(self.ui, 'btnSettings'):
                self.ui.btnSettings.setChecked(index == 4)
        except Exception as e:
            print(f"[UI] Page switch error: {e}")

    def setup_connections(self):
        """Setup signal-slot connections for UI elements."""
        try:
            # Connect main control buttons
            if hasattr(self, "btnArm") and self.btnArm:
                self.btnArm.clicked.connect(self.toggle_arm)

            if hasattr(self, "btnEmergencyStop") and self.btnEmergencyStop:
                self.btnEmergencyStop.clicked.connect(self.emergency_stop)

            # Connect media buttons
            if hasattr(self, "btnCaptureImage") and self.btnCaptureImage:
                self.btnCaptureImage.clicked.connect(self.capture_image)

            if hasattr(self, "btnStartRecording") and self.btnStartRecording:
                self.btnStartRecording.clicked.connect(self.toggle_recording)

            # Connect gallery controls
            if hasattr(self.ui, "btnRefreshGallery"):
                self.ui.btnRefreshGallery.clicked.connect(self.load_gallery)

            if hasattr(self.ui, "cmbGalleryFilter"):
                self.ui.cmbGalleryFilter.currentIndexChanged.connect(self.load_gallery)

            # Connect detection toggle if it exists
            if hasattr(self, "btnToggleDetection") and self.btnToggleDetection:
                self.btnToggleDetection.clicked.connect(self.toggle_detection)

            # Connect zoom buttons
            if hasattr(self.ui, "btnZoomIn") and self.ui.btnZoomIn:
                self.ui.btnZoomIn.clicked.connect(self.zoom_in_cameras)

            if hasattr(self.ui, "btnZoomOut") and self.ui.btnZoomOut:
                self.ui.btnZoomOut.clicked.connect(self.zoom_out_cameras)

            print("[UI] [OK] Button connections established")
        except Exception as e:
            print(f"[UI] Connection setup error: {e}")

    def start_camera_feeds(self):
        """Start dual camera feeds with object detection via MJPEG streams."""
        try:
            # Delay heavy imports until needed
            from .workers.cameraWorker import DualCameraManager

            # Get MJPEG stream URLs from config
            stream_url0 = self.config["camera"].get(
                "stream_url0", "http://raspberrypi.local:8080/video_feed"
            )
            stream_url1 = self.config["camera"].get(
                "stream_url1", "http://raspberrypi.local:8081/video_feed"
            )

            print(f"[CAMERAS] Camera 0 URL: {stream_url0}")
            print(f"[CAMERAS] Camera 1 URL: {stream_url1}")

            self.camera_manager = DualCameraManager(stream_url0, stream_url1)

            # Connect camera 0 (port 8080) to MAIN display
            self.camera_manager.camera0.frame_ready.connect(self.update_camera_main)
            self.camera_manager.camera0.error_occurred.connect(self.handle_camera_error)
            self.camera_manager.camera0.status_update.connect(
                self.update_camera_status_main
            )

            # Connect camera 1 (port 8081) to CAM2 display
            self.camera_manager.camera1.frame_ready.connect(self.update_camera_small)
            self.camera_manager.camera1.error_occurred.connect(self.handle_camera_error)
            self.camera_manager.camera1.status_update.connect(
                self.update_camera_status_cam2
            )

            self.camera_manager.start_all()
            print("[CAMERAS] [OK] Dual MJPEG camera feeds started")

            # Setup object detection
            self.setup_object_detection()
        except Exception as e:
            print(f"[CAMERAS] [ERR] Failed to start: {e}")

    def setup_object_detection(self):
        """Setup object detection for both cameras."""
        try:
            print("[DETECTION] Initializing object detection...")

            # Create detector for camera 0 (main camera)
            self.detector0 = CameraDetector(camera_id=0)
            self.detector0.set_mode("face")  # Default: face/eye/smile detection
            print(
                f"[DETECTION] Camera 0 detector created - Mode: {self.detector0.mode}, Enabled: {self.detector0.enabled}"
            )

            # Create detector for camera 1 (secondary camera)
            self.detector1 = CameraDetector(camera_id=1)
            self.detector1.set_mode("face")  # Default: face/eye/smile detection
            print(
                f"[DETECTION] Camera 1 detector created - Mode: {self.detector1.mode}, Enabled: {self.detector1.enabled}"
            )

            # Attach detectors to camera workers
            if self.camera_manager:
                self.camera_manager.camera0.set_detector(self.detector0)
                self.camera_manager.camera1.set_detector(self.detector1)

                # Enable detection by default
                self.camera_manager.camera0.enable_detection()
                self.camera_manager.camera1.enable_detection()

                print("[DETECTION] ✅ Object detection ACTIVE on both cameras")
                print(
                    f"[DETECTION] Camera 0: detection_enabled={self.camera_manager.camera0.detection_enabled}"
                )
                print(
                    f"[DETECTION] Camera 1: detection_enabled={self.camera_manager.camera1.detection_enabled}"
                )
                print("[DETECTION] Mode: Face Detection (Face/Eye/Smile)")
                print(
                    "[DETECTION] You should see 'FACE DETECTION' text on camera feeds"
                )
        except Exception as e:
            print(f"[DETECTION] [ERR] Failed to setup: {e}")
            import traceback

            traceback.print_exc()

    def toggle_detection(self):
        """Toggle object detection on/off."""
        try:
            if self.camera_manager:
                if self.camera_manager.camera0.detection_enabled:
                    self.camera_manager.camera0.disable_detection()
                    self.camera_manager.camera1.disable_detection()
                    print("[DETECTION] Disabled")
                else:
                    self.camera_manager.camera0.enable_detection()
                    self.camera_manager.camera1.enable_detection()
                    print("[DETECTION] Enabled")
        except Exception as e:
            print(f"[DETECTION] Toggle error: {e}")

    def zoom_in_cameras(self):
        """Zoom in on both cameras"""
        try:
            if self.camera_manager:
                self.camera_manager.zoom_in_all()
                zoom_level = self.camera_manager.camera0.zoom_level
                print(f"[ZOOM] Zoomed in to {zoom_level:.2f}x")
        except Exception as e:
            print(f"[ZOOM] Error: {e}")

    def zoom_out_cameras(self):
        """Zoom out on both cameras"""
        try:
            if self.camera_manager:
                self.camera_manager.zoom_out_all()
                zoom_level = self.camera_manager.camera0.zoom_level
                print(f"[ZOOM] Zoomed out to {zoom_level:.2f}x")
        except Exception as e:
            print(f"[ZOOM] Error: {e}")

    def start_sensor_telemetry(self):
        """Start sensor telemetry worker."""
        try:
            self.sensor_worker = SensorTelemetryWorker(
                host=self.config["sensors"]["host"],
                port=self.config["sensors"]["port"],
                protocol=self.config["sensors"]["protocol"],
            )

            self.sensor_worker.data_received.connect(
                self.update_sensor_display, Qt.ConnectionType.QueuedConnection
            )
            self.sensor_worker.connection_status.connect(
                self.handle_sensor_status, Qt.ConnectionType.QueuedConnection
            )

            if hasattr(self.sensor_worker, "error_occurred"):
                self.sensor_worker.error_occurred.connect(
                    self.handle_sensor_error, Qt.ConnectionType.QueuedConnection
                )

            self.sensor_worker.start()
            QApplication.processEvents()

        except Exception as e:
            print(f"[SENSORS] [ERR] Failed to start: {e}")
            import traceback

            traceback.print_exc()

    @pyqtSlot(str)
    def handle_sensor_error(self, error_msg):
        """Handle sensor connection errors."""
        print(f"[SENSORS]  Error: {error_msg}")
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
                print("[PIXHAWK] [OK] Connected")
                if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">Connected</span></p></body></html>'
                    self.lblPixhawkStatus.setText(status_html)
                if hasattr(self, "lblModeStatus") and self.lblModeStatus:
                    mode_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#00d4ff;\">ONLINE</span></p></body></html>"
                    self.lblModeStatus.setText(mode_html)
            else:
                print("[PIXHAWK] [ERR] Connection failed")
                if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">Disconnected</span></p></body></html>'
                    self.lblPixhawkStatus.setText(status_html)
                if hasattr(self, "lblModeStatus") and self.lblModeStatus:
                    mode_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ff5555;\">OFFLINE</span></p></body></html>"
                    self.lblModeStatus.setText(mode_html)
        except Exception as e:
            print(f"[PIXHAWK] [ERR] Error: {e}")
            if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">Error</span></p></body></html>'
                self.lblPixhawkStatus.setText(status_html)

    def init_joystick(self):
        """Initialize joystick controller."""
        try:
            target = self.config.get("joystick_target")
            self.joystick = JoystickController(target_name=target)

            if self.joystick.is_connected():
                print(f"[JOYSTICK] [OK] Connected: {self.joystick.joystick_name}")
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    status_html = f'<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">{self.joystick.joystick_name} - Ready</span></p></body></html>'
                    self.lblJoystickStatus.setText(status_html)
                # Update the joystick value label to show ONLINE
                if hasattr(self, "ui") and hasattr(self.ui, "lblJoystickValue"):
                    value_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#00d4ff;\">ONLINE</span></p></body></html>"
                    self.ui.lblJoystickValue.setText(value_html)
            else:
                print(f"[JOYSTICK]  No joystick connected")
                if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ffa500;">Not Found</span></p></body></html>'
                    self.lblJoystickStatus.setText(status_html)
                # Update the joystick value label to show OFFLINE
                if hasattr(self, "ui") and hasattr(self.ui, "lblJoystickValue"):
                    value_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ff5555;\">OFFLINE</span></p></body></html>"
                    self.ui.lblJoystickValue.setText(value_html)

        except Exception as e:
            print(f"[JOYSTICK] [ERR] Error: {e}")
            if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">Error</span></p></body></html>'
                self.lblJoystickStatus.setText(status_html)
            # Update the joystick value label to show OFFLINE
            if hasattr(self, "ui") and hasattr(self.ui, "lblJoystickValue"):
                value_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ff5555;\">OFFLINE</span></p></body></html>"
                self.ui.lblJoystickValue.setText(value_html)

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

    @pyqtSlot(str)
    def update_camera_status_main(self, status):
        """Update main camera (port 8080) status label."""
        if hasattr(self, "lblCameraMainStatus") and self.lblCameraMainStatus:
            if status == "Connected":
                self.lblCameraMainStatus.setText("Status: Connected")
                self.lblCameraMainStatus.setStyleSheet("QLabel { color: #00d4ff; font-size: 12px; }")
            else:
                self.lblCameraMainStatus.setText("Status: Disconnected")
                self.lblCameraMainStatus.setStyleSheet("QLabel { color: #ff5555; font-size: 12px; }")
        # Fallback to old label if exists
        elif hasattr(self, "lblCam1Status") and self.lblCam1Status:
            if status == "Connected":
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">CAM 1 - Connected</span></p></body></html>'
            else:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">CAM 1 - Disconnected</span></p></body></html>'
            self.lblCam1Status.setText(status_html)

    @pyqtSlot(str)
    def update_camera_status_cam2(self, status):
        """Update secondary camera (port 8081) status label."""
        if hasattr(self, "lblCameraSmallStatus") and self.lblCameraSmallStatus:
            if status == "Connected":
                self.lblCameraSmallStatus.setText("Status: Connected")
                self.lblCameraSmallStatus.setStyleSheet("QLabel { color: #00d4ff; font-size: 12px; }")
            else:
                self.lblCameraSmallStatus.setText("Status: Disconnected")
                self.lblCameraSmallStatus.setStyleSheet("QLabel { color: #ff5555; font-size: 12px; }")
        # Fallback to old label if exists
        elif hasattr(self, "lblCam2Status") and self.lblCam2Status:
            if status == "Connected":
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">CAM 2 - Connected</span></p></body></html>'
            else:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">CAM 2 - Disconnected</span></p></body></html>'
            self.lblCam2Status.setText(status_html)

    def update_time_display(self):
        """Update the time display in the top bar."""
        try:
            from datetime import datetime
            if hasattr(self.ui, 'lblTime'):
                current_time = datetime.now().strftime("%H:%M:%S")
                self.ui.lblTime.setText(current_time)
        except Exception as e:
            print(f"[UI] Time update error: {e}")

    @pyqtSlot(dict)
    def update_sensor_display(self, data):
        """Update sensor display with new data."""
        try:
            # Update sensor values in Overview tab
            if hasattr(self.ui, 'lblDepthValue'):
                depth = data.get("depth", 0.0)
                self.ui.lblDepthValue.setText(f"{depth:.2f} m")
            
            if hasattr(self.ui, 'lblTemperatureValue'):
                temp = data.get("temperature", 0.0)
                self.ui.lblTemperatureValue.setText(f"{temp:.1f} °C")
            
            if hasattr(self.ui, 'lblPressureValue'):
                pressure = data.get("pressure", 0.0)
                self.ui.lblPressureValue.setText(f"{pressure:.2f} bar")
            
            if hasattr(self.ui, 'lblBatteryValue'):
                battery = data.get("battery", 0)
                self.ui.lblBatteryValue.setText(f"{battery}%")
                # Update battery color based on level
                if battery > 50:
                    self.ui.lblBatteryValue.setStyleSheet("QLabel { color: #00ff00; font-size: 14px; font-weight: bold; }")
                elif battery > 20:
                    self.ui.lblBatteryValue.setStyleSheet("QLabel { color: #ffb800; font-size: 14px; font-weight: bold; }")
                else:
                    self.ui.lblBatteryValue.setStyleSheet("QLabel { color: #ff5555; font-size: 14px; font-weight: bold; }")
            
            # Legacy support for old labels
            if hasattr(self, "lblDepth") and self.lblDepth:
                # Format for new UI with HTML styling
                depth_html = f'<html><head/><body><p><span style=" font-family:\'Consolas\'; font-size:16pt; font-weight:600; color:#00d4ff;">{data["depth"]:.1f}</span><span style=" font-family:\'Consolas\'; font-size:10pt; color:#808080;"> m</span></p></body></html>'
                self.lblDepth.setText(depth_html)

                # Also update the depth label in attitude section
                if hasattr(self, "lblDepthLabel") and self.lblDepthLabel:
                    depth_label_html = f'<html><head/><body><p><span style=" font-family:\'Consolas\'; font-size:11pt; font-weight:600; color:#00d4ff;">{data["depth"]:.1f}</span><span style=" font-size:9pt; color:#808080;"> m</span></p></body></html>'
                    self.lblDepthLabel.setText(depth_label_html)

            if hasattr(self, "lblTemperature") and self.lblTemperature:
                # Format for new UI with HTML styling
                temp_html = f'<html><head/><body><p><span style=" font-family:\'Consolas\'; font-size:16pt; font-weight:600; color:#00d4ff;">{data["temperature"]:.1f}</span><span style=" font-family:\'Consolas\'; font-size:10pt; color:#808080;"> °C</span></p></body></html>'
                self.lblTemperature.setText(temp_html)

            if hasattr(self, "lblPressure") and self.lblPressure:
                # Format for new UI with HTML styling
                # Convert hPa to bar (1 bar = 1000 hPa) for consistency with UI design
                pressure_bar = data["pressure"] / 1000.0
                pressure_html = f"<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:16pt; font-weight:600; color:#00d4ff;\">{pressure_bar:.2f}</span><span style=\" font-family:'Consolas'; font-size:10pt; color:#808080;\"> bar</span></p></body></html>"
                self.lblPressure.setText(pressure_html)

            # Force immediate UI update
            QApplication.processEvents()

        except Exception as e:
            print(f"[UI]  Error updating sensor display: {e}")

    def update_attitude_display(self, heading=None, pitch=None, roll=None):
        """Update the attitude/compass display with current orientation data."""
        try:
            # Update stored values
            if heading is not None:
                self.current_heading = heading
            if pitch is not None:
                self.current_pitch = pitch
            if roll is not None:
                self.current_roll = roll

            # Update compass widget
            if hasattr(self, "compass_widget") and self.compass_widget:
                self.compass_widget.heading = self.current_heading

            # Update heading display
            if hasattr(self, "lblHeadingDisplay") and self.lblHeadingDisplay:
                heading_html = f'<html><head/><body><p align="center"><span style=" font-family:\'Consolas\'; font-size:16pt; font-weight:600; color:#ea8a35;">{self.current_heading:.1f}°</span></p><p align="center"><span style=" font-size:9pt; color:#808080;">North</span></p></body></html>'
                self.lblHeadingDisplay.setText(heading_html)

            # Update pitch display
            if hasattr(self, "lblPitchValue") and self.lblPitchValue:
                pitch_color = "#00d4ff" if abs(self.current_pitch) < 15 else "#ffa500"
                pitch_html = f"<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:14pt; font-weight:600; color:{pitch_color};\">{self.current_pitch:.1f}°</span></p></body></html>"
                self.lblPitchValue.setText(pitch_html)

            # Update roll display
            if hasattr(self, "lblRollValue") and self.lblRollValue:
                roll_color = "#00d4ff" if abs(self.current_roll) < 15 else "#ffa500"
                roll_html = f"<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:14pt; font-weight:600; color:{roll_color};\">{self.current_roll:.1f}°</span></p></body></html>"
                self.lblRollValue.setText(roll_html)

        except Exception as e:
            print(f"[ATTITUDE] Error updating display: {e}")

    def update_attitude_from_pixhawk(self):
        """Fetch and update attitude data from Pixhawk."""
        try:
            # Only update if Pixhawk is connected
            if not self.pixhawk or not self.pixhawk.connected:
                return

            # Get attitude data from Pixhawk
            attitude_data = self.pixhawk.get_attitude()

            if attitude_data and attitude_data.get("connected"):
                # Update the display with new attitude data
                self.update_attitude_display(
                    heading=attitude_data.get("heading"),
                    pitch=attitude_data.get("pitch"),
                    roll=attitude_data.get("roll"),
                )
        except Exception as e:
            # Silently fail - this runs frequently
            pass

    @pyqtSlot(bool)
    def handle_sensor_status(self, connected):
        """Handle sensor connection status changes."""
        status_text = "Sensors: Connected" if connected else "Sensors: Disconnected"
        status_color = "#00d4ff" if connected else "#ff5555"
        print(f"[SENSORS] {'[OK]' if connected else '[ERR]'} {status_text}")

        # Update UI label with HTML formatting for new UI
        if hasattr(self, "lblSensorStatus") and self.lblSensorStatus:
            if connected:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">Connected</span></p></body></html>'
                self.lblSensorStatus.setText(status_html)
            else:
                status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">Disconnected</span></p></body></html>'
                self.lblSensorStatus.setText(status_html)

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
                self.conn_label.setText(f" Network: {pi_host} (Connected)")
                self.conn_label.setStyleSheet("color: #00d4ff;")  # Cyan for connected
            else:
                self.conn_label.setText(" Network: Disconnected")
                self.conn_label.setStyleSheet("color: #ff5555;")  # Red for disconnected

    @pyqtSlot(str)
    def handle_camera_error(self, error_msg):
        """Handle camera errors."""
        print(f"[CAMERA ERROR] {error_msg}")

    def control_loop(self):
        """Main control loop - read joystick and send to Pixhawk."""
        try:
            if not self.joystick or not self.joystick.is_ready():
                return

            if not hasattr(self, "_last_pixhawk_check"):
                self._last_pixhawk_check = 0
                self._pixhawk_connected = False

            current_time = time.time()
            if current_time - self._last_pixhawk_check > 2.0:
                try:
                    self._pixhawk_connected = (
                        self.pixhawk and self.pixhawk.check_connection()
                    )
                except KeyboardInterrupt:
                    raise
                except Exception:
                    self._pixhawk_connected = False
                self._last_pixhawk_check = current_time

            if not self._pixhawk_connected:
                return

            joystick_state = self.joystick.read_joystick()
            channels = self.joystick.compute_thruster_channels(joystick_state)

            if self.armed:
                self.pixhawk.send_rc_channels_override(channels)
            else:
                if not hasattr(self, "_last_arm_warning"):
                    self._last_arm_warning = 0
                if time.time() - self._last_arm_warning > 5.0:
                    if any(abs(ch - 1500) > 10 for ch in channels):
                        print(
                            "[CONTROL]  Commands calculated but NOT sent - System not ARMED!"
                        )
                        print(
                            f"[CONTROL]  Click 'ARM THRUSTERS' button to enable thruster control"
                        )
                        self._last_arm_warning = time.time()

            self.thruster_values = channels

        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[CONTROL]  Control loop error: {e}")

    def update_ui(self):
        """Periodic UI updates - display controller and thruster status."""
        try:
            if not hasattr(self, "_ui_cache_pixhawk"):
                self._ui_cache_pixhawk = False
                self._ui_cache_joystick = False

            # Update Pixhawk status with HTML formatting
            if hasattr(self, "lblPixhawkStatus") and self.lblPixhawkStatus:
                is_connected = getattr(self, "_pixhawk_connected", False)

                if is_connected:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">Connected</span></p></body></html>'
                    self.lblPixhawkStatus.setText(status_html)
                else:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">Disconnected</span></p></body></html>'
                    self.lblPixhawkStatus.setText(status_html)

            # Update Pixhawk value label (ONLINE/OFFLINE)
            if hasattr(self, "lblModeStatus") and self.lblModeStatus:
                is_connected = getattr(self, "_pixhawk_connected", False)
                if is_connected:
                    mode_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#00d4ff;\">ONLINE</span></p></body></html>"
                    self.lblModeStatus.setText(mode_html)
                else:
                    mode_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ff5555;\">OFFLINE</span></p></body></html>"
                    self.lblModeStatus.setText(mode_html)

            # Update Joystick status with HTML formatting
            if hasattr(self, "lblJoystickStatus") and self.lblJoystickStatus:
                if self.joystick and self.joystick.is_connected():
                    ready_text = (
                        "Ready" if self.joystick.is_ready() else "Calibrating..."
                    )
                    joystick_name = self.joystick.joystick_name or "Controller"
                    status_html = f'<html><head/><body><p><span style=" font-size:8pt; color:#00d4ff;">{joystick_name} - {ready_text}</span></p></body></html>'
                    self.lblJoystickStatus.setText(status_html)

                    # Also update the joystick value label to show ONLINE
                    if hasattr(self, "ui") and hasattr(self.ui, "lblJoystickValue"):
                        value_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#00d4ff;\">ONLINE</span></p></body></html>"
                        self.ui.lblJoystickValue.setText(value_html)
                else:
                    status_html = '<html><head/><body><p><span style=" font-size:8pt; color:#ff5555;">No Input Device</span></p></body></html>'
                    self.lblJoystickStatus.setText(status_html)

                    # Also update the joystick value label to show OFFLINE
                    if hasattr(self, "ui") and hasattr(self.ui, "lblJoystickValue"):
                        value_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ff5555;\">OFFLINE</span></p></body></html>"
                        self.ui.lblJoystickValue.setText(value_html)

        except Exception as e:
            print(f"[UI]  Update error: {e}")

    def toggle_arm(self):
        """Toggle arm/disarm state."""
        if not self.pixhawk or not self.pixhawk.connected:
            print("[ARM] Cannot arm: Pixhawk not connected")
            return

        if self.armed:
            if self.pixhawk.disarm():
                self.armed = False
                if hasattr(self, "lblArmStatus"):
                    status_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#ffa500;\">IDLE</span></p></body></html>"
                    self.lblArmStatus.setText(status_html)
                if hasattr(self, "btnArm"):
                    self.btnArm.setText("🚀 ARM THRUSTERS")
                print("[ARM]  Disarmed")
        else:
            if self.pixhawk.arm():
                self.armed = True
                if hasattr(self, "lblArmStatus"):
                    status_html = "<html><head/><body><p><span style=\" font-family:'Consolas'; font-size:11pt; font-weight:600; color:#00d4ff;\">ARMED</span></p></body></html>"
                    self.lblArmStatus.setText(status_html)
                if hasattr(self, "btnArm"):
                    self.btnArm.setText("⚠️ DISARM")
                print("[ARM] [OK] Armed - CAUTION!")

    def emergency_stop(self):
        """Emergency stop - disarm and neutral all thrusters."""
        print("[EMERGENCY]  EMERGENCY STOP ACTIVATED")

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
            print(f"[MANUAL]  Cannot send {direction} command: Pixhawk not connected")
            return

        if not self.armed:
            print(f"[MANUAL]  Cannot send {direction} command: System not armed")
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
            print("[MANUAL]  Forward command sent")

        elif direction == "backward":
            # Backward thrusters
            channels[0] = 1400  # Reverse power
            channels[1] = 1400
            print("[MANUAL]  Backward command sent")

        elif direction == "left":
            # Left strafe (differential thrust)
            channels[2] = 1400  # Left power
            channels[3] = 1600
            print("[MANUAL]  Left command sent")

        elif direction == "right":
            # Right strafe
            channels[2] = 1600  # Right power
            channels[3] = 1400
            print("[MANUAL]  Right command sent")

        # Send the command
        try:
            self.pixhawk.send_rc_channels_override(channels)
        except Exception as e:
            print(f"[MANUAL] [ERR] Error sending command: {e}")

    def stop_manual_command(self):
        """Stop manual command when button released (send neutral)."""
        if not self.pixhawk or not self.pixhawk.connected or not self.armed:
            return

        # Send neutral commands to stop thrusters
        neutral = [1500] * 8
        try:
            self.pixhawk.send_rc_channels_override(neutral)
            print("[MANUAL] ⏹ Manual command stopped (neutral)")
        except Exception as e:
            print(f"[MANUAL] [ERR] Error stopping command: {e}")

    def toggle_detection(self):
        """Toggle object detection on all cameras."""
        self.camera_detection_enabled = not self.camera_detection_enabled

        if self.camera_manager:
            self.camera_manager.toggle_all_detection(self.camera_detection_enabled)

        status = "ON" if self.camera_detection_enabled else "OFF"
        print(f"[DETECTION] Object detection: {status}")

    def open_camera_settings(self):
        """Open camera configuration dialog."""
        # Simple info dialog for camera settings
        from PyQt6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Camera Settings",
            "Camera configuration is managed in config.json.\n\n"
            "Default pipelines:\n"
            "- Pipeline 0 (Camera 1): UDP port 5000\n"
            "- Pipeline 1 (Camera 2): UDP port 5001\n\n"
            "Edit config.json to modify camera streams.",
            QMessageBox.StandardButton.Ok,
        )

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
            print("[CONFIG] [OK] Camera configuration saved")
        except Exception as e:
            print(f"[CONFIG] [ERR] Failed to save: {e}")

    def restart_camera_feeds(self):
        """Restart camera feeds with new configuration (non-blocking)."""
        print("[CAMERAS] Restarting camera feeds...")

        # Stop existing cameras
        if self.camera_manager:
            self.camera_manager.stop_all()
            self.camera_manager = None

        # Use QTimer to avoid blocking the UI
        QTimer.singleShot(500, self._restart_camera_feeds_continue)

    def _restart_camera_feeds_continue(self):
        # Start new cameras with updated config
        self.start_camera_feeds()
        print("[CAMERAS] [OK] Camera feeds restarted")

    def capture_image(self):
        """Capture image from main camera (port 8080)."""
        if not self.camera_manager:
            print("[MEDIA] [ERR] Camera manager not initialized")
            return

        try:
            # Use camera0 (port 8080) - the main camera feed
            camera = self.camera_manager.camera0
            frame = camera.get_frame()

            if frame is not None:
                filepath = self.media_manager.capture_image(frame, camera_id=0)
                if filepath:
                    from PyQt6.QtWidgets import QMessageBox

                    QMessageBox.information(
                        self, "Capture Complete", f"Image saved to:\n{filepath}"
                    )
                    print(f"[MEDIA] [OK] Image captured: {filepath}")
            else:
                print("[MEDIA]  No frame available for capture")
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    "Capture Failed",
                    "No camera frame available.\nPlease ensure camera is connected.",
                )
        except Exception as e:
            print(f"[MEDIA] [ERR] Capture failed: {e}")

    def toggle_recording(self):
        """Toggle video recording on/off from main camera (port 8080)."""
        if not self.camera_manager:
            print("[MEDIA] [ERR] Camera manager not initialized")
            return

        try:
            # Check if already recording
            if self.media_manager.is_recording():
                self.stop_recording()
                return

            # Use camera0 (port 8080) - the main camera feed
            camera = self.camera_manager.camera0
            frame = camera.get_frame()

            if frame is None:
                print("[MEDIA]  No frame available for recording")
                from PyQt6.QtWidgets import QMessageBox

                QMessageBox.warning(
                    self,
                    "Recording Failed",
                    "No camera frame available.\nPlease ensure camera is connected.",
                )
                return

            # Get frame dimensions
            height, width = frame.shape[:2]

            if self.media_manager.start_recording(width, height, 30, camera_id=0):
                # Update button states
                if hasattr(self, "btnStartRecording"):
                    self.btnStartRecording.setText("⏹ STOP")
                    self.btnStartRecording.setStyleSheet(
                        """
                        QPushButton {
                            background-color: #d32f2f;
                            color: white;
                            border: none;
                            border-radius: 6px;
                            padding: 10px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #f44336;
                        }
                    """
                    )

                self.recording_timer = QTimer(self)
                self.recording_timer.timeout.connect(self._write_recording_frame)
                self.recording_timer.start(33)  # ~30 FPS

                print("[MEDIA] [OK] Recording started")
        except Exception as e:
            print(f"[MEDIA] [ERR] Toggle recording failed: {e}")
            import traceback

            traceback.print_exc()

    def stop_recording(self):
        """Stop video recording."""
        if not self.media_manager.is_recording():
            print("[MEDIA]  No recording in progress")
            return

        try:
            if self.recording_timer:
                self.recording_timer.stop()
                self.recording_timer = None

            filepath = self.media_manager.stop_recording()

            # Restore button appearance
            if hasattr(self, "btnStartRecording"):
                self.btnStartRecording.setText("⏺ RECORD")
                self.btnStartRecording.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #FF8800;
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #FFA040;
                    }
                """
                )

            if filepath:
                from PyQt6.QtWidgets import QMessageBox

                msg = f"Video saved to:\n{filepath}"
                QMessageBox.information(self, "Recording Complete", msg)
            print(f"[MEDIA] [OK] Recording stopped: {filepath}")
        except Exception as e:
            print(f"[MEDIA] [ERR] Stop recording failed: {e}")

    def load_gallery(self):
        """Load media files from the media folder and display in gallery."""
        try:
            from pathlib import Path
            from PyQt6.QtWidgets import (
                QFrame,
                QVBoxLayout,
                QLabel,
                QPushButton,
                QWidget,
            )
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QPixmap
            import os

            print("[GALLERY] Loading gallery...")

            # Get filter selection
            filter_type = "All"
            if hasattr(self.ui, "cmbGalleryFilter"):
                filter_text = self.ui.cmbGalleryFilter.currentText()
                print(f"[GALLERY] Filter: {filter_text}")

                # Handle emoji-based filter text
                if "All" in filter_text or "📁" in filter_text:
                    filter_type = "All"
                elif "Image" in filter_text or "📷" in filter_text:
                    filter_type = "Images"
                elif "Video" in filter_text or "🎥" in filter_text:
                    filter_type = "Videos"
                else:
                    filter_type = filter_text  # Fallback to original text

                print(f"[GALLERY] Resolved filter type: {filter_type}")

            # Get media directory - use absolute path
            media_dir = Path(__file__).parent.parent.parent / "media"
            images_dir = media_dir / "images"
            videos_dir = media_dir / "videos"

            print(f"[GALLERY] Media dir: {media_dir}")
            print(f"[GALLERY] Images dir exists: {images_dir.exists()}")
            print(f"[GALLERY] Videos dir exists: {videos_dir.exists()}")

            # Ensure directories exist
            images_dir.mkdir(parents=True, exist_ok=True)
            videos_dir.mkdir(parents=True, exist_ok=True)

            # Collect media files - use set to avoid duplicates
            media_files_set = set()

            print(f"[GALLERY] Searching for files with filter_type: {filter_type}")

            if filter_type in ["All", "Images"]:
                print(f"[GALLERY] Scanning images directory: {images_dir}")
                if images_dir.exists():
                    # Use case-insensitive matching - only lowercase patterns
                    for ext in ["*.png", "*.jpg", "*.jpeg"]:
                        found_files = list(images_dir.glob(ext))
                        print(f"[GALLERY]   {ext}: {len(found_files)} files")
                        for f in found_files:
                            print(f"[GALLERY]     - {f.name}")
                            media_files_set.add((f, "image"))
                else:
                    print(f"[GALLERY] Images directory does not exist!")

            if filter_type in ["All", "Videos"]:
                print(f"[GALLERY] Scanning videos directory: {videos_dir}")
                if videos_dir.exists():
                    # Use case-insensitive matching - only lowercase patterns
                    for ext in ["*.mp4", "*.avi", "*.mov"]:
                        found_files = list(videos_dir.glob(ext))
                        print(f"[GALLERY]   {ext}: {len(found_files)} files")
                        for f in found_files:
                            media_files_set.add((f, "video"))
                else:
                    print(f"[GALLERY] Videos directory does not exist!")

            # Convert set back to list
            media_files = list(media_files_set)
            print(f"[GALLERY] Total unique media files found: {len(media_files)}")

            # Sort by modification time (newest first)
            media_files.sort(key=lambda x: x[0].stat().st_mtime, reverse=True)

            # Check if gallery grid exists
            if not hasattr(self.ui, "gridLayout_gallery"):
                print("[GALLERY] [ERR] gridLayout_gallery not found in UI")
                return

            gallery_grid = self.ui.gridLayout_gallery

            # Remove all existing items except lblGalleryEmpty
            items_to_remove = []
            for i in range(gallery_grid.count()):
                item = gallery_grid.itemAt(i)
                if item and item.widget():
                    widget = item.widget()
                    # Don't delete the empty label
                    if widget.objectName() != "lblGalleryEmpty":
                        items_to_remove.append(widget)

            # Delete the collected items
            for widget in items_to_remove:
                gallery_grid.removeWidget(widget)
                widget.deleteLater()

            # Show/hide empty message
            if hasattr(self.ui, "lblGalleryEmpty"):
                if len(media_files) == 0:
                    try:
                        self.ui.lblGalleryEmpty.setText(
                            "No media files found.\nCapture images or record videos to see them here."
                        )
                        self.ui.lblGalleryEmpty.show()
                        print("[GALLERY] No media files - showing empty message")
                    except RuntimeError as e:
                        print(f"[GALLERY] Warning: Could not update empty label: {e}")
                    return
                else:
                    try:
                        self.ui.lblGalleryEmpty.hide()
                    except RuntimeError:
                        pass  # Label might have been deleted

            # Add media items to gallery
            items_per_row = 4
            for idx, (file_path, file_type) in enumerate(media_files):
                row = idx // items_per_row
                col = idx % items_per_row

                # Create gallery item frame
                frame = QFrame()
                frame.setMinimumSize(250, 200)
                frame.setMaximumSize(250, 200)
                frame.setObjectName(f"gallery_item_frame_{idx}")
                frame.setStyleSheet(
                    """
                    QFrame {
                        background-color: #1a1a1a;
                        border: 1px solid #2a2a2a;
                        border-radius: 8px;
                    }
                    QFrame:hover {
                        border: 1px solid #FF8800;
                        background-color: #252525;
                    }
                """
                )

                layout = QVBoxLayout(frame)
                layout.setContentsMargins(8, 8, 8, 8)
                layout.setSpacing(8)

                # Create preview label
                preview_label = QLabel()
                preview_label.setMinimumSize(234, 150)
                preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                preview_label.setStyleSheet(
                    "background-color: #0a0a0a; border-radius: 4px;"
                )

                if file_type == "image":
                    # Load and display image thumbnail
                    try:
                        pixmap = QPixmap(str(file_path))
                        if not pixmap.isNull():
                            scaled_pixmap = pixmap.scaled(
                                234,
                                150,
                                Qt.AspectRatioMode.KeepAspectRatio,
                                Qt.TransformationMode.SmoothTransformation,
                            )
                            preview_label.setPixmap(scaled_pixmap)
                            print(f"[GALLERY] Loaded image thumbnail: {file_path.name}")
                        else:
                            preview_label.setText("📷 Image")
                            print(f"[GALLERY] Failed to load image: {file_path.name}")
                    except Exception as img_err:
                        print(
                            f"[GALLERY] Error loading image {file_path.name}: {img_err}"
                        )
                        preview_label.setText("📷 Image")
                else:
                    # Video placeholder
                    preview_label.setText("🎥 Video")
                    preview_label.setStyleSheet(
                        """
                        background-color: #0a0a0a; 
                        border-radius: 4px;
                        color: #FF8800;
                        font-size: 24pt;
                    """
                    )

                layout.addWidget(preview_label)

                # Create title label with filename
                title_label = QLabel(file_path.name)
                title_label.setStyleSheet("color: #ffffff; font-size: 9pt;")
                title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                title_label.setWordWrap(True)
                layout.addWidget(title_label)

                # Make frame clickable to open file
                frame.mousePressEvent = (
                    lambda event, path=file_path: self.open_media_file(path)
                )

                # Add to grid
                gallery_grid.addWidget(frame, row, col)
                print(
                    f"[GALLERY] Added item {idx}: {file_path.name} at row={row}, col={col}"
                )

            print(f"[GALLERY] [OK] Loaded {len(media_files)} media files successfully")

        except Exception as e:
            print(f"[GALLERY] [ERR] Failed to load gallery: {e}")
            import traceback

            traceback.print_exc()

    def open_media_file(self, file_path):
        """Open media file with default system application."""
        try:
            import os
            import platform

            if platform.system() == "Windows":
                os.startfile(file_path)
            elif platform.system() == "Darwin":  # macOS
                os.system(f'open "{file_path}"')
            else:  # Linux
                os.system(f'xdg-open "{file_path}"')

            print(f"[GALLERY] Opening: {file_path.name}")
        except Exception as e:
            print(f"[GALLERY] [ERR] Failed to open file: {e}")

    def setup_mission_logs(self):
        """Setup Mission Logs page functionality."""
        try:
            # Connect filter buttons
            if hasattr(self.ui, 'btnFilterAll'):
                self.ui.btnFilterAll.clicked.connect(lambda: self.filter_logs('all'))
            if hasattr(self.ui, 'btnFilterInfo'):
                self.ui.btnFilterInfo.clicked.connect(lambda: self.filter_logs('info'))
            if hasattr(self.ui, 'btnFilterWarning'):
                self.ui.btnFilterWarning.clicked.connect(lambda: self.filter_logs('warning'))
            if hasattr(self.ui, 'btnFilterError'):
                self.ui.btnFilterError.clicked.connect(lambda: self.filter_logs('error'))
            
            # Connect search
            if hasattr(self.ui, 'txtSearchLogs'):
                self.ui.txtSearchLogs.textChanged.connect(self.search_logs)
            
            # Connect export button
            if hasattr(self.ui, 'btnExportLogs'):
                self.ui.btnExportLogs.clicked.connect(self.export_logs)
            
            # Initialize log entries list
            self.mission_logs = []
            self.filtered_logs = []
            self.current_filter = 'all'
            
            print("[MISSION LOGS] Setup complete")
        except Exception as e:
            print(f"[MISSION LOGS] Setup error: {e}")

    def load_mission_logs(self):
        """Load and display mission logs."""
        try:
            from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
            from PyQt6.QtCore import Qt
            from datetime import datetime
            
            # Sample log entries matching the design
            sample_logs = [
                {"type": "info", "timestamp": "2025-11-30 10:15:23", "category": "System", "message": "ROV system initialized successfully"},
                {"type": "info", "timestamp": "2025-11-30 10:15:45", "category": "Thrusters", "message": "All 8 thrusters calibrated and ready"},
                {"type": "info", "timestamp": "2025-11-30 10:16:12", "category": "Camera", "message": "Camera systems online - 3 feeds active"},
                {"type": "warning", "timestamp": "2025-11-30 10:18:30", "category": "Thrusters", "message": "Thruster 3 power fluctuation detected"},
                {"type": "info", "timestamp": "2025-11-30 10:20:05", "category": "Navigation", "message": "Descent to 12.5m depth initiated"},
                {"type": "warning", "timestamp": "2025-11-30 10:22:15", "category": "Power", "message": "Battery level at 75%"},
                {"type": "info", "timestamp": "2025-11-30 10:25:40", "category": "Tools", "message": "Image captured - IMG_001.jpg"},
                {"type": "info", "timestamp": "2025-11-30 10:26:10", "category": "Tools", "message": "Video recording started - VID_001.mp4"},
                {"type": "info", "timestamp": "2025-11-30 10:28:22", "category": "Navigation", "message": "Auto-hold position engaged"},
                {"type": "info", "timestamp": "2025-11-30 10:30:05", "category": "Tools", "message": "Sample collection tool activated"},
                {"type": "warning", "timestamp": "2025-11-30 10:32:18", "category": "Sensors", "message": "Water temperature dropped to 16.2°C"},
                {"type": "info", "timestamp": "2025-11-30 10:35:45", "category": "Navigation", "message": "Waypoint WP_005 saved"},
                {"type": "error", "timestamp": "2025-11-30 10:38:12", "category": "Communications", "message": "Communication latency spike detected - 250ms"},
                {"type": "warning", "timestamp": "2025-11-30 10:40:30", "category": "Power", "message": "Battery level at 50% - consider surfacing soon"},
                {"type": "info", "timestamp": "2025-11-30 10:42:55", "category": "Navigation", "message": "Ascending to 8m depth"},
            ]
            
            # Store logs
            self.mission_logs = sample_logs
            self.filtered_logs = sample_logs.copy()
            
            # Clear existing log entries
            if hasattr(self.ui, 'verticalLayout_logsList'):
                layout = self.ui.verticalLayout_logsList
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
            
            # Create log entry widgets
            for log in self.filtered_logs:
                self.create_log_entry(log)
            
            print(f"[MISSION LOGS] Loaded {len(self.filtered_logs)} log entries")
        except Exception as e:
            print(f"[MISSION LOGS] Load error: {e}")
            import traceback
            traceback.print_exc()

    def create_log_entry(self, log):
        """Create a single log entry widget."""
        try:
            from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
            from PyQt6.QtCore import Qt
            
            # Determine icon and colors based on log type
            if log["type"] == "info":
                icon = "ℹ️"
                entry_class = "logEntryInfo"
                icon_color = "#00d4ff"
            elif log["type"] == "warning":
                icon = "⚠️"
                entry_class = "logEntryWarning"
                icon_color = "#ffb800"
            else:  # error
                icon = "❌"
                entry_class = "logEntryError"
                icon_color = "#ff4444"
            
            # Determine category tag color
            category_class = "categoryTag"
            if log["category"] == "Power":
                category_class = "categoryTagPower"
            elif log["category"] == "Communications":
                category_class = "categoryTagCommunications"
            
            # Create main frame
            import uuid
            unique_id = str(uuid.uuid4())[:8]
            log_frame = QFrame()
            log_frame.setObjectName(f"logEntry_{unique_id}")
            log_frame.setStyleSheet(f"""
                QFrame#logEntry_{unique_id} {{
                    background-color: {'rgba(255, 184, 0, 0.1)' if log['type'] == 'warning' else ('rgba(255, 68, 68, 0.1)' if log['type'] == 'error' else '#1a1d2e')};
                    border: 1px solid {'rgba(255, 184, 0, 0.3)' if log['type'] == 'warning' else ('rgba(255, 68, 68, 0.3)' if log['type'] == 'error' else '#2a2d3e')};
                    border-left: 4px solid {icon_color};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            
            # Create horizontal layout
            h_layout = QHBoxLayout(log_frame)
            h_layout.setSpacing(12)
            h_layout.setContentsMargins(16, 16, 16, 16)
            
            # Icon label
            icon_label = QLabel(icon)
            icon_label.setStyleSheet(f"color: {icon_color}; font-size: 20px;")
            icon_label.setFixedWidth(30)
            h_layout.addWidget(icon_label)
            
            # Content layout
            content_layout = QVBoxLayout()
            content_layout.setSpacing(8)
            
            # Top row: timestamp and category
            top_layout = QHBoxLayout()
            top_layout.setSpacing(12)
            
            timestamp_label = QLabel(log["timestamp"])
            timestamp_label.setStyleSheet("color: #8b949e; font-size: 12px;")
            top_layout.addWidget(timestamp_label)
            
            top_layout.addStretch()
            
            category_label = QLabel(log["category"])
            category_style = f"""
                background-color: {'rgba(255, 184, 0, 0.2)' if log['category'] == 'Power' else ('rgba(255, 68, 68, 0.2)' if log['category'] == 'Communications' else '#1e3a5f')};
                color: {'#ffb800' if log['category'] == 'Power' else ('#ff4444' if log['category'] == 'Communications' else '#00d4ff')};
                border-radius: 12px;
                padding: 4px 12px;
                font-size: 11px;
                font-weight: bold;
            """
            category_label.setStyleSheet(category_style)
            top_layout.addWidget(category_label)
            
            content_layout.addLayout(top_layout)
            
            # Message label
            message_label = QLabel(log["message"])
            message_label.setStyleSheet("color: #ffffff; font-size: 14px;")
            message_label.setWordWrap(True)
            content_layout.addWidget(message_label)
            
            h_layout.addLayout(content_layout, 1)
            
            # Add to logs list
            if hasattr(self.ui, 'verticalLayout_logsList'):
                self.ui.verticalLayout_logsList.addWidget(log_frame)
            
        except Exception as e:
            print(f"[MISSION LOGS] Create entry error: {e}")

    def filter_logs(self, filter_type):
        """Filter logs by type."""
        try:
            self.current_filter = filter_type
            
            # Update button states
            if hasattr(self.ui, 'btnFilterAll'):
                self.ui.btnFilterAll.setChecked(filter_type == 'all')
            if hasattr(self.ui, 'btnFilterInfo'):
                self.ui.btnFilterInfo.setChecked(filter_type == 'info')
            if hasattr(self.ui, 'btnFilterWarning'):
                self.ui.btnFilterWarning.setChecked(filter_type == 'warning')
            if hasattr(self.ui, 'btnFilterError'):
                self.ui.btnFilterError.setChecked(filter_type == 'error')
            
            # Filter logs
            if filter_type == 'all':
                self.filtered_logs = self.mission_logs.copy()
            else:
                self.filtered_logs = [log for log in self.mission_logs if log["type"] == filter_type]
            
            # Reload display
            if hasattr(self.ui, 'verticalLayout_logsList'):
                layout = self.ui.verticalLayout_logsList
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                for log in self.filtered_logs:
                    self.create_log_entry(log)
            
            print(f"[MISSION LOGS] Filtered to {len(self.filtered_logs)} {filter_type} logs")
        except Exception as e:
            print(f"[MISSION LOGS] Filter error: {e}")

    def search_logs(self, search_text):
        """Search logs by text."""
        try:
            search_lower = search_text.lower()
            
            # Filter by search text
            if search_lower:
                filtered = [log for log in self.mission_logs 
                           if search_lower in log["message"].lower() 
                           or search_lower in log["category"].lower()]
            else:
                filtered = self.mission_logs.copy()
            
            # Apply current type filter
            if self.current_filter != 'all':
                filtered = [log for log in filtered if log["type"] == self.current_filter]
            
            self.filtered_logs = filtered
            
            # Reload display
            if hasattr(self.ui, 'verticalLayout_logsList'):
                layout = self.ui.verticalLayout_logsList
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                for log in self.filtered_logs:
                    self.create_log_entry(log)
        except Exception as e:
            print(f"[MISSION LOGS] Search error: {e}")

    def export_logs(self):
        """Export logs to file."""
        try:
            from PyQt6.QtWidgets import QFileDialog
            from datetime import datetime
            import json
            
            filename, _ = QFileDialog.getSaveFileName(
                self, "Export Logs", f"mission_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                "JSON Files (*.json);;All Files (*)"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.mission_logs, f, indent=2)
                print(f"[MISSION LOGS] Exported {len(self.mission_logs)} logs to {filename}")
        except Exception as e:
            print(f"[MISSION LOGS] Export error: {e}")

    def _write_recording_frame(self):
        """Write frame to video during recording from main camera (port 8080)."""
        if not self.media_manager.is_recording():
            return

        try:
            # Use camera0 (port 8080) - the main camera feed
            camera = self.camera_manager.camera0
            frame = camera.get_frame()
            if frame is not None:
                self.media_manager.write_frame(frame)
        except Exception as e:
            print(f"[MEDIA] [ERR] Failed to write frame: {e}")

    def open_media_folder(self):
        """Open media folder in file explorer."""
        try:
            media_path = self.media_manager.get_media_path()
            import subprocess
            import platform

            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{media_path}"')
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", media_path])
            else:
                subprocess.Popen(["xdg-open", media_path])

            print(f"[MEDIA] [OK] Opened media folder: {media_path}")
        except Exception as e:
            print(f"[MEDIA] [ERR] Failed to open folder: {e}")

    def closeEvent(self, event):
        """Clean up on window close."""
        print("[MARINER] Shutting down...")

        # Stop timers
        self.control_timer.stop()
        self.ui_update_timer.stop()

        if self.recording_timer:
            self.recording_timer.stop()

        # Stop media recording if active (no stop method in MediaManager, so skip)

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

        print("[MARINER] [OK] Shutdown complete")
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
