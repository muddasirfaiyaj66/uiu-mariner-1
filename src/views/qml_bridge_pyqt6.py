"""
UIU MARINER - QML Bridge Module (PyQt6 Version)
================================================
PyQt6 backend that connects QML UI to all ROV functionality.
Uses PyQt6 instead of PySide6 to avoid DLL conflicts.

Features:
  - Camera feed integration from multiple sources
  - MAVLink/Pixhawk telemetry and control
  - Sensor data display (depth, temperature, etc.)
  - Joystick control integration
  - Media capture and recording
  - Real-time data updates via Qt signals/slots

Author: UIU MARINER Development Team
"""

import sys
import os
from pathlib import Path
from PyQt6.QtCore import (QObject, pyqtSignal as Signal, pyqtSlot as Slot, 
                          pyqtProperty as Property, QTimer, QUrl, Qt, QThread)
from PyQt6.QtGui import QGuiApplication, QImage, QPixmap
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtQuick import QQuickImageProvider
import numpy as np
import cv2
import json
import time
import threading

# Import ROV components - avoid importing mainWindow to prevent conflicts
try:
    import sys
    from pathlib import Path
    parent_path = Path(__file__).parent.parent.parent
    if str(parent_path) not in sys.path:
        sys.path.insert(0, str(parent_path))
    
    from src.services.mavlinkConnection import PixhawkConnection
    from src.joystickController import JoystickController
    from src.computer_vision.camera_detector import CameraDetector
    
    # Import workers directly to avoid mainWindow
    import importlib.util
    
    # Load camera worker
    camera_worker_path = Path(__file__).parent / "workers" / "cameraWorker.py"
    spec = importlib.util.spec_from_file_location("cameraWorker", camera_worker_path)
    camera_worker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(camera_worker_module)
    CameraWorker = camera_worker_module.CameraWorker
    
    # Load sensor worker
    sensor_worker_path = Path(__file__).parent / "workers" / "sensorWorker.py"
    spec = importlib.util.spec_from_file_location("sensorWorker", sensor_worker_path)
    sensor_worker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sensor_worker_module)
    SensorTelemetryWorker = sensor_worker_module.SensorTelemetryWorker
    
    # Load media manager
    media_manager_path = Path(__file__).parent / "workers" / "mediaManager.py"
    spec = importlib.util.spec_from_file_location("mediaManager", media_manager_path)
    media_manager_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(media_manager_module)
    MediaManager = media_manager_module.MediaManager
    
except Exception as e:
    print(f"[Import Error] {e}")
    import traceback
    traceback.print_exc()
    # Provide fallback classes for testing
    class CameraWorker:
        def __init__(self, *args, **kwargs):
            pass
    class SensorTelemetryWorker:
        def __init__(self, *args, **kwargs):
            pass
    class MediaManager:
        def __init__(self, *args, **kwargs):
            pass
    class PixhawkConnection:
        def __init__(self, *args, **kwargs):
            pass
    class JoystickController:
        def __init__(self, *args, **kwargs):
            pass
    class CameraDetector:
        def __init__(self, *args, **kwargs):
            pass
        def set_mode(self, mode):
            pass
        def enable(self):
            pass


class CameraImageProvider(QQuickImageProvider):
    """
    Custom image provider for camera feeds in QML.
    Allows QML to display camera frames via Image source URL.
    """
    
    def __init__(self):
        super().__init__(QQuickImageProvider.ImageType.Pixmap)
        self.pixmap = QPixmap(640, 480)
        self.pixmap.fill(Qt.GlobalColor.black)
    
    def requestPixmap(self, id, requestedSize):
        """Return the current camera frame pixmap - PyQt6 signature"""
        # PyQt6 has different signature than PySide6 (no size parameter)
        return self.pixmap, self.pixmap.size()
    
    def updatePixmap(self, pixmap):
        """Update the current frame"""
        if pixmap and not pixmap.isNull():
            self.pixmap = pixmap


class ROVBackend(QObject):
    """
    Main backend class that bridges QML UI with Python ROV functionality.
    Exposes properties and signals that QML can bind to for real-time updates.
    """
    
    # Signals for QML property changes (PyQt6 syntax)
    compassHeadingChanged = Signal(float)
    depthChanged = Signal(float)
    temperatureChanged = Signal(float)
    salinityChanged = Signal(float)
    phLevelChanged = Signal(float)
    oxygenChanged = Signal(float)
    turbidityChanged = Signal(float)
    thrusterArmedChanged = Signal(bool)
    connectionStatusChanged = Signal(str)
    activeCameraChanged = Signal(int)
    isRecordingChanged = Signal(bool)
    
    # Camera signals
    cameraFrameUpdated = Signal(int)  # camera_id
    cameraStatusChanged = Signal(int, str)  # camera_id, status
    
    # Media signals
    imageCaptured = Signal(str)  # filename
    videoSaved = Signal(str)  # filename
    mediaFilesChanged = Signal()  # Emitted when gallery needs refresh
    
    # Connection status signals
    piConnectedChanged = Signal(bool)
    pixhawkConnectedChanged = Signal(bool)
    joystickConnectedChanged = Signal(bool)
    detectionEnabledChanged = Signal(bool)
    
    # Mission timer signal
    toggleMissionTimer = Signal()
    
    def __init__(self):
        super().__init__()
        
        # Configuration
        self.config = self._load_config()
        
        # State variables
        self._compass_heading = 0.0
        self._depth = 0.0
        self._temperature = 0.0
        self._salinity = 35.0
        self._ph_level = 8.2
        self._oxygen = 7.8
        self._turbidity = 15.3
        self._thruster_armed = False
        self._connection_status = "Disconnected"
        self._active_camera = 0
        self._is_recording = False
        self._pi_connected = False
        self._pixhawk_connected = False
        self._joystick_connected = False
        self._detection_enabled = True  # Object detection enabled by default
        
        # Components (initialized later)
        self.pixhawk = None
        self.joystick = None
        self.sensor_worker = None
        self.media_manager = None
        self.camera_workers = []
        self.camera_providers = []
        
        # Control loop timer
        self.control_timer = QTimer()
        self.control_timer.timeout.connect(self._control_loop)
        self.control_timer.setInterval(50)  # 20 Hz
        
        # UI update timer
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self._update_ui)
        self.ui_timer.setInterval(100)  # 10 Hz
        
        print("[ROV Backend] Initialized (PyQt6)")
    
    def _load_config(self):
        """Load configuration from config.json"""
        config_path = Path(__file__).parent.parent.parent / "config.json"
        default_config = {
            "mavlink_connection": "tcp:raspberrypi.local:7000",
            "camera": {
                "stream_url0": "http://raspberrypi.local:8080/video_feed",
                "stream_url1": "http://raspberrypi.local:8081/video_feed",
            },
            "sensors": {
                "host": "raspberrypi.local",
                "port": 5002,
                "protocol": "tcp",
            },
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return {**default_config, **json.load(f)}
        except Exception as e:
            print(f"[Config] Error loading: {e}, using defaults")
        
        return default_config
    
    # ======================== Properties for QML (PyQt6 syntax) ========================
    
    def getCompassHeading(self):
        return self._compass_heading
    
    def setCompassHeading(self, value):
        if self._compass_heading != value:
            self._compass_heading = value
            self.compassHeadingChanged.emit(value)
    
    compassHeading = Property(float, getCompassHeading, setCompassHeading, notify=compassHeadingChanged)
    
    def getDepth(self):
        return self._depth
    
    def setDepth(self, value):
        if self._depth != value:
            self._depth = value
            self.depthChanged.emit(value)
    
    depth = Property(float, getDepth, setDepth, notify=depthChanged)
    
    def getTemperature(self):
        return self._temperature
    
    def setTemperature(self, value):
        if self._temperature != value:
            self._temperature = value
            self.temperatureChanged.emit(value)
    
    temperature = Property(float, getTemperature, setTemperature, notify=temperatureChanged)
    
    def getSalinity(self):
        return self._salinity
    
    def setSalinity(self, value):
        if self._salinity != value:
            self._salinity = value
            self.salinityChanged.emit(value)
    
    salinity = Property(float, getSalinity, setSalinity, notify=salinityChanged)
    
    def getPhLevel(self):
        return self._ph_level
    
    def setPhLevel(self, value):
        if self._ph_level != value:
            self._ph_level = value
            self.phLevelChanged.emit(value)
    
    phLevel = Property(float, getPhLevel, setPhLevel, notify=phLevelChanged)
    
    def getOxygen(self):
        return self._oxygen
    
    def setOxygen(self, value):
        if self._oxygen != value:
            self._oxygen = value
            self.oxygenChanged.emit(value)
    
    oxygen = Property(float, getOxygen, setOxygen, notify=oxygenChanged)
    
    def getTurbidity(self):
        return self._turbidity
    
    def setTurbidity(self, value):
        if self._turbidity != value:
            self._turbidity = value
            self.turbidityChanged.emit(value)
    
    turbidity = Property(float, getTurbidity, setTurbidity, notify=turbidityChanged)
    
    def getThrusterArmed(self):
        return self._thruster_armed
    
    def setThrusterArmed(self, value):
        if self._thruster_armed != value:
            self._thruster_armed = value
            self.thrusterArmedChanged.emit(value)
            print(f"[ROV] Thrusters {'ARMED' if value else 'DISARMED'}")
    
    thrusterArmed = Property(bool, getThrusterArmed, setThrusterArmed, notify=thrusterArmedChanged)
    
    def getConnectionStatus(self):
        return self._connection_status
    
    def setConnectionStatus(self, value):
        if self._connection_status != value:
            self._connection_status = value
            self.connectionStatusChanged.emit(value)
    
    connectionStatus = Property(str, getConnectionStatus, setConnectionStatus, notify=connectionStatusChanged)
    
    def getPiConnected(self):
        return self._pi_connected
    
    def setPiConnected(self, value):
        if self._pi_connected != value:
            self._pi_connected = value
            self.piConnectedChanged.emit(value)
    
    piConnected = Property(bool, getPiConnected, setPiConnected, notify=piConnectedChanged)
    
    def getPixhawkConnected(self):
        return self._pixhawk_connected
    
    def setPixhawkConnected(self, value):
        if self._pixhawk_connected != value:
            self._pixhawk_connected = value
            self.pixhawkConnectedChanged.emit(value)
    
    pixhawkConnected = Property(bool, getPixhawkConnected, setPixhawkConnected, notify=pixhawkConnectedChanged)
    
    def getJoystickConnected(self):
        return self._joystick_connected
    
    def setJoystickConnected(self, value):
        if self._joystick_connected != value:
            self._joystick_connected = value
            self.joystickConnectedChanged.emit(value)
    
    joystickConnected = Property(bool, getJoystickConnected, setJoystickConnected, notify=joystickConnectedChanged)
    
    def getDetectionEnabled(self):
        return self._detection_enabled
    
    def setDetectionEnabled(self, value):
        if self._detection_enabled != value:
            self._detection_enabled = value
            self.detectionEnabledChanged.emit(value)
            print(f"[Detection] Object detection {'ENABLED' if value else 'DISABLED'}")
            # Update camera workers
            for worker in self.camera_workers:
                if value:
                    worker.enable_detection()
                else:
                    worker.disable_detection()
    
    detectionEnabled = Property(bool, getDetectionEnabled, setDetectionEnabled, notify=detectionEnabledChanged)
    
    @Slot()
    def toggleDetection(self):
        """Toggle object detection on/off"""
        self.setDetectionEnabled(not self._detection_enabled)
    
    def getActiveCamera(self):
        return self._active_camera
    
    def setActiveCamera(self, value):
        if self._active_camera != value:
            self._active_camera = value
            self.activeCameraChanged.emit(value)
            print(f"[ROV] Active camera: {value}")
    
    activeCamera = Property(int, getActiveCamera, setActiveCamera, notify=activeCameraChanged)
    
    def getIsRecording(self):
        return self._is_recording
    
    def setIsRecording(self, value):
        if self._is_recording != value:
            self._is_recording = value
            self.isRecordingChanged.emit(value)
            if value:
                self._start_recording()
            else:
                self._stop_recording()
    
    isRecording = Property(bool, getIsRecording, setIsRecording, notify=isRecordingChanged)
    
    # ======================== Initialization ========================
    
    @Slot()
    def initializeComponents(self):
        """Initialize all ROV components (call after QML is loaded)"""
        try:
            print("[ROV] Initializing components...")
            
            # Start timers immediately
            self.ui_timer.start()
            self.control_timer.start()
            
            # Priority 1: Initialize Pi-dependent components immediately (cameras, sensors)
            QTimer.singleShot(50, self._init_cameras)
            QTimer.singleShot(100, self._init_sensors)
            
            # Priority 2: Initialize local components (joystick, media)
            QTimer.singleShot(150, self._init_joystick)
            QTimer.singleShot(200, self._init_media_manager)
            
            # Priority 3: Initialize Pixhawk last (has 10s timeout, runs in background)
            QTimer.singleShot(250, self._init_pixhawk)
            
            print("[ROV] Component initialization scheduled")
        except Exception as e:
            print(f"[ROV] Error during initialization: {e}")
            import traceback
            traceback.print_exc()
    
    def _init_cameras(self):
        """Initialize camera feeds - must run on main thread for Qt signals"""
        try:
            print("[Cameras] Initializing camera streams...")
            
            # Create detectors for object detection
            self.detector0 = CameraDetector(camera_id=0)
            self.detector0.set_mode("contour")
            self.detector0.enable()
            
            self.detector1 = CameraDetector(camera_id=1)
            self.detector1.set_mode("contour")
            self.detector1.enable()
            
            # Camera 0 - Main camera
            url0 = self.config["camera"]["stream_url0"]
            worker0 = CameraWorker(url0, camera_id=0, flip_horizontal=True)
            worker0.set_detector(self.detector0)
            worker0.enable_detection()
            worker0.frame_ready.connect(lambda pixmap: self._on_camera_frame(0, pixmap))
            worker0.status_update.connect(lambda status: self._on_camera_status(0, status))
            worker0.start()
            self.camera_workers.append(worker0)
            
            # Camera 1 - Secondary camera
            url1 = self.config["camera"]["stream_url1"]
            worker1 = CameraWorker(url1, camera_id=1, flip_horizontal=True)
            worker1.set_detector(self.detector1)
            worker1.enable_detection()
            worker1.frame_ready.connect(lambda pixmap: self._on_camera_frame(1, pixmap))
            worker1.status_update.connect(lambda status: self._on_camera_status(1, status))
            worker1.start()
            self.camera_workers.append(worker1)
            
            print("[Cameras] Camera workers started with OBJECT DETECTION enabled")
            # Cameras connect to Pi, so mark Pi as connected
            self.setPiConnected(True)
        except Exception as e:
            print(f"[Cameras] Initialization error: {e}")
            import traceback
            traceback.print_exc()
    
    def _init_sensors(self):
        """Initialize sensor telemetry - must run on main thread for Qt signals"""
        try:
            print("[Sensors] Initializing sensor connection...")
            
            host = self.config["sensors"]["host"]
            port = self.config["sensors"]["port"]
            protocol = self.config["sensors"]["protocol"]
            
            self.sensor_worker = SensorTelemetryWorker(
                host=host, 
                port=port, 
                protocol=protocol,
                auto_mock_fallback=False
            )
            self.sensor_worker.data_received.connect(self._on_sensor_data)
            self.sensor_worker.connection_status.connect(self._on_sensor_connection)
            self.sensor_worker.start()
            
            print("[Sensors] Sensor worker started")
            # Sensors connect to Pi, confirm Pi connection
            self.setPiConnected(True)
        except Exception as e:
            print(f"[Sensors] Initialization error: {e}")
    
    def _init_pixhawk(self):
        """Initialize Pixhawk connection in background thread to avoid blocking UI"""
        def connect_pixhawk():
            try:
                print("[Pixhawk] Connecting to vehicle (background thread)...")
                
                connection_string = self.config["mavlink_connection"]
                self.pixhawk = PixhawkConnection(connection_string)
                
                # Attempt connection (may take up to 10 seconds)
                self.pixhawk.connect()
                
                # Check actual connection status
                if self.pixhawk.check_connection():
                    self.setConnectionStatus("Connected")
                    self.setPixhawkConnected(True)
                    print("[Pixhawk] ✅ Connected and verified")
                else:
                    self.setConnectionStatus("Disconnected")
                    self.setPixhawkConnected(False)
                    print("[Pixhawk] ⚠ Connection attempt completed, no heartbeat detected")
                    print("[Pixhawk] Status will update automatically when connection is established")
            except Exception as e:
                print(f"[Pixhawk] Connection error: {e}")
                self.setConnectionStatus("Error")
                self.setPixhawkConnected(False)
        
        # Run connection in background thread so UI stays responsive
        connection_thread = threading.Thread(target=connect_pixhawk, daemon=True)
        connection_thread.start()
        print("[Pixhawk] Connection attempt started in background")
    
    def _init_joystick(self):
        """Initialize joystick controller"""
        try:
            print("[Joystick] Initializing controller...")
            
            self.joystick = JoystickController(joystick_index=0)
            
            # Check if connected (not is_ready which has calibration delay)
            if self.joystick.is_connected():
                self.setJoystickConnected(True)
                print(f"[Joystick] ✅ Controller connected: {self.joystick.joystick_name}")
            else:
                self.setJoystickConnected(False)
                print("[Joystick] ⚠ No controller detected")
        except Exception as e:
            print(f"[Joystick] Initialization error: {e}")
            self.setJoystickConnected(False)
    
    def _init_media_manager(self):
        """Initialize media manager"""
        try:
            print("[Media] Initializing media manager...")
            self.media_manager = MediaManager()
            print("[Media] ✅ Media manager ready")
        except Exception as e:
            print(f"[Media] Initialization error: {e}")
    
    # ======================== Callbacks ========================
    
    def _on_camera_frame(self, camera_id, pixmap):
        """Handle new camera frame"""
        if camera_id < len(self.camera_providers):
            self.camera_providers[camera_id].updatePixmap(pixmap)
            self.cameraFrameUpdated.emit(camera_id)
    
    def _on_camera_status(self, camera_id, status):
        """Handle camera status change"""
        print(f"[Camera {camera_id}] Status: {status}")
        self.cameraStatusChanged.emit(camera_id, status)
    
    def _on_sensor_data(self, data):
        """Handle sensor data update"""
        try:
            updated = []
            if "depth" in data:
                self.setDepth(float(data["depth"]))
                updated.append(f"depth={data['depth']}")
            if "temperature" in data:
                self.setTemperature(float(data["temperature"]))
                updated.append(f"temp={data['temperature']}")
            if "salinity" in data:
                self.setSalinity(float(data["salinity"]))
                updated.append(f"salinity={data['salinity']}")
            if "ph" in data:
                self.setPhLevel(float(data["ph"]))
                updated.append(f"pH={data['ph']}")
            if "oxygen" in data:
                self.setOxygen(float(data["oxygen"]))
                updated.append(f"O2={data['oxygen']}")
            if "turbidity" in data:
                self.setTurbidity(float(data["turbidity"]))
                updated.append(f"turbidity={data['turbidity']}")
            
            if updated:
                print(f"[Sensors] Updated: {', '.join(updated)}")
        except Exception as e:
            print(f"[Sensors] Data parsing error: {e}")
    
    def _on_sensor_connection(self, connected):
        """Handle sensor connection status"""
        status = "Connected" if connected else "Disconnected"
        print(f"[Sensors] Connection status: {status}")
    
    # ======================== Control Loop ========================
    
    def _control_loop(self):
        """Main control loop - handles joystick input and vehicle control"""
        try:
            # Check and update Pixhawk connection status
            if self.pixhawk:
                is_connected = self.pixhawk.check_connection()
                if is_connected != self._pixhawk_connected:
                    self.setPixhawkConnected(is_connected)
                    status_text = "Connected" if is_connected else "Disconnected"
                    print(f"[UI] Pixhawk status changed: {status_text}")

            # Debug: Print control loop tick
            print(f"[DEBUG] Control loop tick. Armed: {self._thruster_armed}, Connected: {getattr(self.pixhawk, 'connected', False)}")

            if self.joystick and self.joystick.is_ready():
                state = self.joystick.read_joystick()
                # Handle joystick button actions
                self._handle_joystick_buttons(state)

                if self._thruster_armed and self.pixhawk and self.pixhawk.vehicle:
                    # Debug: Print MANUAL_CONTROL about to be sent
                    manual_ctrl = self.joystick.compute_manual_control(state)
                    print(f"[DEBUG] Sending MANUAL_CONTROL: x={manual_ctrl['x']} y={manual_ctrl['y']} z={manual_ctrl['z']} r={manual_ctrl['r']} (should see thruster movement if armed)")
                    self.pixhawk.send_manual_control(
                        x=manual_ctrl["x"],
                        y=manual_ctrl["y"],
                        z=manual_ctrl["z"],
                        r=manual_ctrl["r"],
                        buttons=manual_ctrl["buttons"]
                    )
                    # Debug: Print RC_CHANNELS_OVERRIDE about to be sent
                    channels = self.joystick.compute_thruster_channels(state)
                    print(f"[DEBUG] Sending RC_CHANNELS_OVERRIDE: {channels}")
                    self.pixhawk.send_rc_channels_override(channels)
                else:
                    print(f"[DEBUG] Not sending control: Armed={self._thruster_armed}, Pixhawk={self.pixhawk is not None}, Vehicle={getattr(self.pixhawk, 'vehicle', None) is not None}")

            if self.pixhawk and self.pixhawk.vehicle:
                try:
                    attitude = self.pixhawk.vehicle.messages.get("ATTITUDE")
                    if attitude:
                        yaw = attitude.yaw * 57.2958
                        self.setCompassHeading((yaw + 360) % 360)
                except Exception:
                    pass
        except Exception as e:
            print(f"[Control Loop] Error: {e}")
    
    def _handle_joystick_buttons(self, state):
        """
        Handle joystick button presses for special functions:
        - Button 6 (Back): Arm/Disarm thrusters
        - Button 7 (Start): Cycle through cameras (0->1->2->3->0)
        - Button 3 (Y): Toggle mission timer on/off
        - Button 0 (A): Capture picture
        - Button 1 (B): Toggle recording
        - Button 2 (X): Emergency stop (handled in compute_thruster_channels)
        - Camera Zoom: Axis 5 (RT) zoom in, Axis 4 (LT) zoom out
        """
        buttons = state.get("buttons", {})
        
        # Track button states to detect single press (not hold)
        if not hasattr(self, '_last_button_states'):
            self._last_button_states = {}
        
        # Button 6: Toggle Arm/Disarm - call toggleArm() to also send command to Pixhawk
        if buttons.get("btn6", False) and not self._last_button_states.get("btn6", False):
            self.toggleArm()  # This updates state AND sends command to Pixhawk
            print(f"[Joystick] Button 6: Thrusters {'ARMED' if self._thruster_armed else 'DISARMED'}")
        
        # Button 7: Cycle through cameras
        if buttons.get("btn7", False) and not self._last_button_states.get("btn7", False):
            next_camera = (self._active_camera + 1) % 4
            self.setActiveCamera(next_camera)
            camera_names = ["Front", "Bottom", "Port", "Starboard"]
            print(f"[Joystick] Button 7: Switched to Camera {next_camera + 1} ({camera_names[next_camera]})")
        
        # Button 3: Toggle mission timer
        if buttons.get("btn3", False) and not self._last_button_states.get("btn3", False):
            self.toggleMissionTimer.emit()
            print("[Joystick] Button 3: Mission timer toggled")
        
        # Button 0: Capture picture
        if buttons.get("btn0", False) and not self._last_button_states.get("btn0", False):
            print("[Joystick] Button 0: Capturing image...")
            self.captureImage()
        
        # Button 1: Toggle recording
        if buttons.get("btn1", False) and not self._last_button_states.get("btn1", False):
            self.setIsRecording(not self._is_recording)
            print(f"[Joystick] Button 1: Recording {'STARTED' if self._is_recording else 'STOPPED'}")
        
        # Camera Zoom (Axis 5 = zoom in, Axis 4 = zoom out)
        if self.joystick and hasattr(self.joystick, 'camera_zoom_in'):
            if self.joystick.camera_zoom_in and self.camera_workers:
                worker = self.camera_workers[self._active_camera]
                worker.zoom_in()
            elif self.joystick.camera_zoom_out and self.camera_workers:
                worker = self.camera_workers[self._active_camera]
                worker.zoom_out()
        
        # Update button states for next iteration
        self._last_button_states = buttons.copy()
    
    def _update_ui(self):
        """Update UI elements periodically"""
        # Print current values every 5 seconds for debugging
        import time
        if not hasattr(self, '_last_debug_time'):
            self._last_debug_time = 0
        
        current_time = time.time()
        if current_time - self._last_debug_time > 5:
            print(f"[UI Debug] Depth: {self._depth:.1f}m, Temp: {self._temperature:.1f}°C, Compass: {self._compass_heading:.1f}°, Armed: {self._thruster_armed}")
            self._last_debug_time = current_time
    
    # ======================== Slots for QML ========================
    
    @Slot()
    def toggleArm(self):
        """Toggle thruster armed state"""
        self.setThrusterArmed(not self._thruster_armed)

        print(f"[DEBUG] toggleArm called. Now armed: {self._thruster_armed}")

        if self.pixhawk and self.pixhawk.vehicle:
            if self._thruster_armed:
                # CRITICAL: Set MANUAL mode BEFORE arming!
                print("[ARM] Setting MANUAL mode before arming...")
                mode_result = self.pixhawk.set_mode("MANUAL")
                print(f"[DEBUG] set_mode('MANUAL') result: {mode_result}")
                print("[ARM] Arming thrusters (force=True)...")
                arm_result = self.pixhawk.arm(force=True)
                print(f"[DEBUG] arm(force=True) result: {arm_result}")
            else:
                print("[ARM] Disarming thrusters...")
                disarm_result = self.pixhawk.disarm()
                print(f"[DEBUG] disarm() result: {disarm_result}")
    
    @Slot()
    def captureImage(self):
        """Capture a still image"""
        print("[Media] Capturing image...")
        try:
            if self.media_manager and self.camera_workers:
                worker = self.camera_workers[self._active_camera]
                if worker.current_frame is not None:
                    filename = self.media_manager.capture_image(worker.current_frame, self._active_camera)
                    if filename:
                        print(f"[Media] ✅ Image saved: {filename}")
                        self.imageCaptured.emit(filename)
                        self.mediaFilesChanged.emit()  # Refresh gallery
                    else:
                        print("[Media] ❌ Image capture failed")
                else:
                    print("[Media] ❌ No frame available from camera")
        except Exception as e:
            print(f"[Media] Image capture error: {e}")
    
    @Slot()
    def testUpdate(self):
        """Test method to update values and verify UI is responding"""
        import random
        self.setDepth(random.uniform(0, 100))
        self.setTemperature(random.uniform(10, 30))
        self.setCompassHeading(random.uniform(0, 360))
        print(f"[Test] Updated values - Depth: {self._depth:.1f}, Temp: {self._temperature:.1f}, Compass: {self._compass_heading:.1f}")
    
    def _start_recording(self):
        """Start video recording"""
        print("[Media] Starting recording...")
        try:
            if self.media_manager and self.camera_workers:
                worker = self.camera_workers[self._active_camera]
                if worker.current_frame is not None:
                    # Get frame dimensions from current frame
                    h, w = worker.current_frame.shape[:2]
                    self.media_manager.start_recording(w, h, 30, self._active_camera)
                    
                    # Start recording timer to write frames continuously
                    if not hasattr(self, 'recording_timer'):
                        self.recording_timer = QTimer()
                        self.recording_timer.timeout.connect(self._write_recording_frame)
                    self.recording_timer.start(33)  # ~30 fps
                    print(f"[Media] ✅ Recording started")
                else:
                    print("[Media] ❌ No frame available from camera")
        except Exception as e:
            print(f"[Media] Recording start error: {e}")
    
    def _stop_recording(self):
        """Stop video recording"""
        print("[Media] Stopping recording...")
        try:
            # Stop recording timer
            if hasattr(self, 'recording_timer'):
                self.recording_timer.stop()
            
            if self.media_manager:
                filename = self.media_manager.stop_recording()
                if filename:
                    print(f"[Media] ✅ Recording saved: {filename}")
                    self.videoSaved.emit(filename)
                    self.mediaFilesChanged.emit()  # Refresh gallery
                else:
                    print("[Media] ⚠️ Recording stopped but no file saved")
        except Exception as e:
            print(f"[Media] Recording stop error: {e}")
    
    def _write_recording_frame(self):
        """Write current frame to video during recording"""
        try:
            if self.media_manager and self.camera_workers and self.media_manager.is_recording():
                worker = self.camera_workers[self._active_camera]
                if worker.current_frame is not None:
                    self.media_manager.write_frame(worker.current_frame)
        except Exception as e:
            print(f"[Media] Frame write error: {e}")
    
    @Slot(result='QVariantList')
    def getMediaFiles(self):
        """Get list of all media files (images and videos)"""
        files = []
        try:
            # Get media path - use media_manager if available, otherwise construct directly
            if self.media_manager:
                media_path = Path(self.media_manager.get_media_path())
            else:
                # Fallback: construct path directly
                media_path = Path(__file__).parent.parent.parent / "media"
            
            print(f"[Media] Loading files from: {media_path}")
            
            # Get images
            images_dir = media_path / "images"
            if images_dir.exists():
                for img in sorted(images_dir.glob("*.png"), reverse=True):
                    stat = img.stat()
                    # Convert Windows path to file:/// URL for QML
                    file_url = QUrl.fromLocalFile(str(img)).toString()
                    files.append({
                        'type': 'photo',
                        'path': str(img),
                        'url': file_url,
                        'name': img.name,
                        'size': stat.st_size,
                        'timestamp': stat.st_mtime
                    })
            
            # Get videos
            videos_dir = media_path / "videos"
            if videos_dir.exists():
                for vid in sorted(videos_dir.glob("*.mp4"), reverse=True):
                    stat = vid.stat()
                    # Convert Windows path to file:/// URL for QML
                    file_url = QUrl.fromLocalFile(str(vid)).toString()
                    files.append({
                        'type': 'video',
                        'path': str(vid),
                        'url': file_url,
                        'name': vid.name,
                        'size': stat.st_size,
                        'timestamp': stat.st_mtime
                    })
            
            # Sort by timestamp (newest first)
            files.sort(key=lambda x: x['timestamp'], reverse=True)
            print(f"[Media] Found {len(files)} media files")
        except Exception as e:
            print(f"[Media] Error getting media files: {e}")
            import traceback
            traceback.print_exc()
        
        return files
    
    @Slot(result='QVariantMap')
    def getMediaStats(self):
        """Get media statistics (counts and sizes)"""
        stats = {
            'photos_count': 0,
            'photos_size': 0,
            'videos_count': 0,
            'videos_size': 0
        }
        
        try:
            # Get media path - use media_manager if available, otherwise construct directly
            if self.media_manager:
                media_path = Path(self.media_manager.get_media_path())
            else:
                # Fallback: construct path directly
                media_path = Path(__file__).parent.parent.parent / "media"
            
            # Count images
            images_dir = media_path / "images"
            if images_dir.exists():
                for img in images_dir.glob("*.png"):
                    stats['photos_count'] += 1
                    stats['photos_size'] += img.stat().st_size
            
            # Count videos
            videos_dir = media_path / "videos"
            if videos_dir.exists():
                for vid in videos_dir.glob("*.mp4"):
                    stats['videos_count'] += 1
                    stats['videos_size'] += vid.stat().st_size
        except Exception as e:
            print(f"[Media] Error getting media stats: {e}")
        
        return stats
    
    @Slot(str)
    def openMediaFile(self, file_path):
        """Open media file in system default application"""
        try:
            import subprocess
            import platform
            
            file_path = str(file_path)
            if not Path(file_path).exists():
                print(f"[Media] File not found: {file_path}")
                return
            
            print(f"[Media] Opening file: {file_path}")
            
            # Use platform-specific command to open file
            if platform.system() == 'Windows':
                # Windows: use 'start' command
                subprocess.Popen(['start', '', file_path], shell=True)
            elif platform.system() == 'Darwin':
                # macOS: use 'open' command
                subprocess.Popen(['open', file_path])
            else:
                # Linux: use 'xdg-open' command
                subprocess.Popen(['xdg-open', file_path])
            
            print(f"[Media] ✅ File opened successfully")
        except Exception as e:
            print(f"[Media] ❌ Error opening file: {e}")
            import traceback
            traceback.print_exc()
    
    # ======================== Cleanup ========================
    
    def cleanup(self):
        """Cleanup resources before exit"""
        print("[ROV] Cleaning up...")
        
        # Stop timers
        if self.control_timer.isActive():
            self.control_timer.stop()
        if self.ui_timer.isActive():
            self.ui_timer.stop()
        
        # Stop camera workers
        for i, worker in enumerate(self.camera_workers):
            if worker.isRunning():
                print(f"[Camera {i}] Stopping worker...")
                worker.running = False
                worker.quit()
                worker.wait(2000)
        
        # Stop sensor worker
        if self.sensor_worker and self.sensor_worker.isRunning():
            print("[Sensors] Stopping worker...")
            self.sensor_worker.running = False
            self.sensor_worker.quit()
            self.sensor_worker.wait(2000)
        
        # Disarm and disconnect Pixhawk
        if self.pixhawk:
            try:
                if self._thruster_armed:
                    print("[Pixhawk] Disarming...")
                    self.pixhawk.disarm()
                print("[Pixhawk] Disconnecting...")
                self.pixhawk.disconnect()
            except Exception as e:
                print(f"[Pixhawk] Cleanup error: {e}")
        
        print("[ROV] Cleanup complete")


def main():
    """Main entry point for QML-based ROV interface using PyQt6."""
    try:
        app = QGuiApplication(sys.argv)
        app.setApplicationName("UIU MARINER ROV Control")
        app.setOrganizationName("UIU Underwater Robotics")
        
        engine = QQmlApplicationEngine()
        backend = ROVBackend()
        
        print("[ROV Backend] Initialized (PyQt6)")
        
        # Register camera image providers
        for i in range(4):
            provider = CameraImageProvider()
            backend.camera_providers.append(provider)
            engine.addImageProvider(f"camera{i}", provider)
        
        # Expose backend to QML
        engine.rootContext().setContextProperty("backend", backend)
        
        # Load QML file
        qml_file = Path(__file__).parent / "main.qml"
        engine.load(QUrl.fromLocalFile(str(qml_file)))
        
        if not engine.rootObjects():
            print("[QML] ERROR: Failed to load QML file")
            return -1
        
        print("[QML] Window loaded successfully")
        
        # Get the root window and force it to show
        root_objects = engine.rootObjects()
        if root_objects:
            window = root_objects[0]
            print(f"[QML] Root object type: {type(window)}")
            print(f"[QML] Window properties - visible: {window.property('visible')}, width: {window.property('width')}, height: {window.property('height')}")
            
            # Force window to show and raise to front
            window.show()
            window.raise_()
            window.requestActivate()
            print("[QML] Window forced to foreground")
        
        # QML will call initializeComponents() via Component.onCompleted
        # Don't call it here to avoid double initialization
        
        # Run the event loop
        print("[QML] Starting application event loop...")
        result = app.exec()
        
        print("[QML] Application closing...")
        backend.cleanup()
        
        return result
    except KeyboardInterrupt:
        print("\n[QML] Application interrupted by user")
        try:
            backend.cleanup()
        except:
            pass
        return 0
    except Exception as e:
        print(f"[QML] Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
