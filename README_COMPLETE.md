# UIU MARINER - Professional ROV Control System 🌊

Complete Remotely Operated Vehicle control software with dual camera feeds, object detection, sensor telemetry, and professional GUI.

![Status](https://img.shields.io/badge/status-production_ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## 🎯 Features

### Core Control

- ✅ **8-Channel Thruster Control** via MAVLink RC_CHANNELS_OVERRIDE
- ✅ **Xbox 360 Joystick Input** with automatic mapping
- ✅ **Pixhawk/ArduSub Integration** (UDP/TCP)
- ✅ **Arm/Disarm Safety System**
- ✅ **Emergency Stop Button**

### Vision System

- 📹 **Dual Camera Feeds** from Raspberry Pi (GStreamer H.264)
- 🎯 **Real-time Object Detection** using Haar Cascade classifiers
- 📊 **FPS Monitoring** with performance overlay
- 🔀 **Camera Switching** between front/bottom views
- 🎨 **Professional Video Overlays** (camera info, detection boxes)

### Telemetry

- 🌡️ **Temperature Monitoring**
- 📏 **Depth Sensor** (pressure-based)
- 📈 **Pressure Readings**
- 🔌 **TCP/UDP Protocol Support**
- 🧪 **Mock Sensor Mode** for testing without hardware

### User Interface

- 💎 **Professional Dark Theme GUI**
- 📱 **Responsive Layout** (1280x720 minimum)
- 🎨 **Qt Designer .ui File** for easy customization
- 📊 **Real-time Status Displays**
- 🚦 **Color-coded Connection Status**

---

## 🚀 Quick Start

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Configure Connection

Edit `config.json`:

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "joystick_target": "xbox",
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  },
  "sensors": {
    "host": "192.168.21.126",
    "port": 5000,
    "protocol": "tcp",
    "mock_mode": false
  }
}
```

### 3. Launch Application

```powershell
python launch_mariner.py
```

Or directly:

```powershell
python src/ui/marinerApp.py
```

---

## 📁 Project Structure

```
mariner-software-1.0/
├── src/
│   ├── connections/
│   │   └── mavlinkConnection.py      # Pixhawk MAVLink communication
│   ├── controllers/
│   │   └── joystickController.py     # Xbox 360 joystick input
│   └── ui/
│       ├── marinerApp.py             # Main application (NEW)
│       ├── cameraWorker.py           # Camera streaming + detection (NEW)
│       ├── sensorWorker.py           # Sensor telemetry (NEW)
│       └── main_window.ui            # Qt Designer UI file
├── media/
│   ├── images/                       # Screenshots
│   └── videos/                       # Demo recordings
├── config.json                       # Configuration file
├── requirements.txt                  # Python dependencies
├── launch_mariner.py                 # Quick launcher (NEW)
└── README_COMPLETE.md                # This file (NEW)
```

---

## 🎮 Controls

### Xbox 360 Joystick Mapping

| Control                | Function          |
| ---------------------- | ----------------- |
| **Left Stick Y**       | Forward/Backward  |
| **Left Stick X**       | Left/Right Strafe |
| **Right Stick Y**      | Up/Down (Depth)   |
| **Right Stick X**      | Yaw Rotation      |
| **RT (Right Trigger)** | Roll Right        |
| **LT (Left Trigger)**  | Roll Left         |
| **A Button**           | Arm/Disarm        |
| **B Button**           | Emergency Stop    |

### Keyboard Shortcuts (GUI)

- **Ctrl+A** - Toggle Arm
- **Ctrl+E** - Emergency Stop
- **Ctrl+D** - Toggle Detection
- **Esc** - Exit Application

---

## 🔧 Configuration

### MAVLink Connection Formats

```python
# UDP (recommended for ArduSub)
"mavlink_connection": "udp:192.168.0.104:14550"

# TCP
"mavlink_connection": "tcp:10.42.0.185:7000"

# Serial (USB)
"mavlink_connection": "COM3"  # Windows
"mavlink_connection": "/dev/ttyUSB0"  # Linux
```

### Camera Pipeline Customization

For different camera setups, modify GStreamer pipelines:

```python
# USB Camera (no GStreamer needed)
"pipeline0": "0"  # Camera index

# RTSP Stream
"pipeline0": "rtspsrc location=rtsp://192.168.1.100:8554/stream ! ..."

# File Playback (testing)
"pipeline0": "filesrc location=test_video.mp4 ! ..."
```

### Sensor Protocols

```python
# TCP (reliable, used in reference code)
"protocol": "tcp"

# UDP (lower latency, less reliable)
"protocol": "udp"
```

---

## 🎯 Object Detection

### Haar Cascade Classifiers

Currently using lightweight Haar Cascade for underwater object detection:

- **Frontal Face Detection** (default, for testing)
- **Custom trained classifiers** can be added

### Adding Custom Detection Models

1. Place `.xml` classifier file in `src/resources/`
2. Update `cameraWorker.py`:

```python
cascade_path = cv2.data.haarcascades + 'your_custom_cascade.xml'
self.cascade = cv2.CascadeClassifier(cascade_path)
```

### Future: YOLO Integration

For more advanced detection, YOLOv8 can be integrated:

```python
# TODO: Replace Haar Cascade with YOLO
from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model(frame)
```

---

## 🧪 Testing Without Hardware

### Mock Mode

Enable mock sensors in `config.json`:

```json
"sensors": {
  "mock_mode": true
}
```

### Test Video Files

Replace camera pipelines with video files:

```json
"camera": {
  "pipeline0": "filesrc location=test_underwater.mp4 ! decodebin ! videoconvert ! appsink"
}
```

### Virtual Joystick

Use keyboard controls when joystick unavailable (future feature).

---

## 📊 System Requirements

### Hardware

- **PC**: Windows 10/11 (8GB+ RAM recommended)
- **Joystick**: Xbox 360 controller (USB or wireless)
- **ROV**: Pixhawk running ArduSub v4.5+
- **Raspberry Pi**: Pi 4 (for cameras and sensors)
- **Network**: WiFi or Ethernet connection to ROV

### Software

- **Python**: 3.8 or higher
- **GStreamer**: 1.18+ (for camera decoding)
- **OpenCV**: 4.8+ with GStreamer support
- **PyQt6**: 6.6.0+

### Network Configuration

```
PC (Control Station)        ROV (Raspberry Pi + Pixhawk)
192.168.0.100        <--->  192.168.0.104:14550 (MAVLink)
                     <--->  192.168.0.104:5000 (Camera 0)
                     <--->  192.168.0.104:5001 (Camera 1)
                     <--->  192.168.21.126:5000 (Sensors)
```

---

## 🐛 Troubleshooting

### Issue: "Pixhawk not connected"

- ✅ Check MAVLink connection string in `config.json`
- ✅ Verify network connectivity: `ping 192.168.0.104`
- ✅ Ensure ArduSub is running on Pixhawk
- ✅ Check firewall settings (allow UDP port 14550)

### Issue: "No camera feed"

- ✅ Verify GStreamer is installed: `gst-inspect-1.0 --version`
- ✅ Test pipeline manually: `gst-launch-1.0 udpsrc port=5000 ! ...`
- ✅ Check camera streaming on Raspberry Pi side
- ✅ Verify network ports 5000/5001 are open

### Issue: "Joystick not detected"

- ✅ Connect Xbox controller before launching app
- ✅ Test with Windows "Set up USB game controllers"
- ✅ Update pygame: `pip install --upgrade pygame`

### Issue: "Sensor data not updating"

- ✅ Enable mock mode for testing: `"mock_mode": true`
- ✅ Check sensor service on Raspberry Pi
- ✅ Verify TCP connection: `telnet 192.168.21.126 5000`

### Issue: "Import errors (cv2, PyQt6, etc.)"

- ✅ Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- ✅ Check Python version: `python --version` (needs 3.8+)
- ✅ Use virtual environment:
  ```powershell
  python -m venv venv
  .\venv\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

---

## 🔒 Safety Features

### Pre-flight Checks

- ✅ Verify Pixhawk connection before arming
- ✅ Check joystick is responding
- ✅ Confirm camera feeds are active
- ✅ Test emergency stop button

### Automatic Safeguards

- 🛡️ **Neutral on disconnect** - Thrusters neutral if MAVLink lost
- 🛡️ **Disarm on error** - Auto-disarm on critical errors
- 🛡️ **Emergency stop** - Instant neutral + disarm
- 🛡️ **Joystick deadzone** - Prevents drift from centered sticks

### Operational Safety

- ⚠️ Always test in **shallow water** first
- ⚠️ Keep **emergency stop** readily accessible
- ⚠️ Monitor **battery voltage** on telemetry
- ⚠️ Have **surface support** during operations

---

## 📈 Performance Optimization

### Camera Settings

```python
# Reduce resolution for lower latency
"pipeline0": "udpsrc port=5000 ! ... ! videoscale ! video/x-raw,width=640,height=480 ! ..."

# Disable detection to increase FPS
camera.set_detection_enabled(False)
```

### Control Loop Tuning

```python
# In marinerApp.py
self.control_timer.start(100)  # 10 Hz (default)
self.control_timer.start(50)   # 20 Hz (more responsive)
self.control_timer.start(33)   # 30 Hz (max recommended)
```

### Network Optimization

- Use **wired Ethernet** instead of WiFi when possible
- Enable **QoS (Quality of Service)** on router for real-time traffic
- Reduce camera **bitrate** if bandwidth limited

---

## 🎓 Architecture Overview

### MVC Pattern

```
Model (Data)              Controller (Logic)         View (UI)
├─ mavlinkConnection     ├─ joystickController      ├─ marinerApp.py
├─ cameraWorker          └─ (business logic)        └─ main_window.ui
└─ sensorWorker
```

### Threading Model

- **Main Thread**: GUI (PyQt6 event loop)
- **Control Thread**: Joystick reading + MAVLink sending (10 Hz)
- **Camera Thread 0**: Camera 0 capture + detection
- **Camera Thread 1**: Camera 1 capture + detection
- **Sensor Thread**: TCP/UDP telemetry reception
- **UI Update Thread**: Status display refresh (2 Hz)

### Signal/Slot Communication

```python
# Camera → GUI
camera.frame_ready.connect(gui.update_camera_display)

# Sensor → GUI
sensor.data_received.connect(gui.update_sensor_display)

# GUI → Controller
btnArm.clicked.connect(controller.toggle_arm)
```

---

## 🚀 Future Enhancements

### Planned Features

- [ ] YOLO object detection integration
- [ ] Recording/playback functionality
- [ ] Mission planning and autonomous modes
- [ ] Multi-ROV support
- [ ] Cloud telemetry logging
- [ ] Mobile app companion (Android/iOS)

### Community Contributions

Want to contribute? Areas we'd love help with:

- **Underwater-specific object detection models**
- **Improved UI/UX design**
- **Performance optimizations**
- **Additional sensor integrations**
- **Documentation translations**

---

## 📜 License

This project is part of UIU's autonomous underwater vehicle research.  
For academic and research use.

---

## 👥 Credits

**UIU MARINER Team**

- Original reference code: Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA
- System architecture: Reorganized and enhanced
- Camera integration: Based on control.py
- Sensor telemetry: Based on sensor.py
- Professional GUI: Complete redesign

**Technologies Used**

- ArduSub - Open-source ROV firmware
- MAVLink - Micro Air Vehicle communication protocol
- PyQt6 - Python GUI framework
- OpenCV - Computer vision library
- GStreamer - Multimedia framework

---

## 📞 Support

**Having issues?**

1. Check the Troubleshooting section above
2. Review existing documentation in `docs/`
3. Test with mock mode enabled
4. Check network connectivity

**System Status Indicators**

- 🟢 Green = Connected/OK
- 🟠 Orange = Standby/Unarmed
- 🔴 Red = Error/Disconnected

---

## 🎉 Ready to Dive!

Your complete ROV control system is ready. Remember:

1. Test all systems on surface first
2. Always have an emergency stop plan
3. Monitor telemetry during operations
4. Keep safety as top priority

**Happy exploring the depths! 🌊🤖**

---

_Last Updated: 2025_  
_Version: 1.0 - Complete Professional System_
