# UIU MARINER

**Ground Station Control Software for Underwater ROV**

## Overview

Control software for an 8-thruster ROV using Pixhawk (ArduSub) flight controller.

**Features:**
- MAVLink communication via TCP/UDP
- Xbox controller support (Mode A - QGC Standard)
- Dual camera feeds from Raspberry Pi
- Real-time telemetry display
- Object detection (OpenCV)

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   Ground PC     │      │  Raspberry Pi   │      │    Pixhawk      │
│  (This Repo)    │◄────►│  (MAVLink Relay)│◄────►│   (ArduSub)     │
├─────────────────┤ TCP  ├─────────────────┤ UART ├─────────────────┤
│ PyQt6 GUI       │ 7000 │ MAVProxy Server │      │ ArduSub v4.5+   │
│ Joystick Input  │      │ Camera Server   │      │ 8x Thrusters    │
│ MAVLink Client  │      │ Sensor Server   │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Installation

```powershell
# Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

## Usage

```powershell
# Launch application (QML interface)
python launch_mariner.py

# Launch legacy widgets interface
python launch_mariner.py --legacy
```

## Joystick Controls (Mode A)

| Control | Function |
|---------|----------|
| Left Stick Y | Up/Down (Throttle) |
| Left Stick X | Yaw (Rotate) |
| Right Stick Y | Forward/Back |
| Right Stick X | Left/Right |
| A Button | Capture Photo |
| B Button | Toggle Video |
| X Button | Emergency Stop |
| Y Button | Timer Toggle |
| Back Button | Arm/Disarm |
| Start Button | Switch Camera |
| LT | Zoom Out |
| RT | Zoom In |

## Project Structure

```
uiu-mariner-1/
├── launch_mariner.py      # Entry point
├── config.json            # Configuration
├── requirements.txt       # Dependencies
├── src/
│   ├── joystickController.py
│   ├── controllers/       # Business logic
│   ├── models/           # Data structures
│   ├── services/         # MAVLink communication
│   ├── views/            # PyQt6 UI
│   └── computer_vision/  # Object detection
└── pi_scripts/           # Raspberry Pi scripts
```

## Configuration

Edit `config.json`:

```json
{
  "mavlink": {
    "connection": "tcp:raspberrypi.local:7000"
  },
  "camera": {
    "stream_url_0": "http://raspberrypi.local:8080/video_feed",
    "stream_url_1": "http://raspberrypi.local:8081/video_feed"
  }
}
```

## Requirements

- Python 3.8+
- Windows 10/11
- Xbox 360 or compatible controller
- Pixhawk with ArduSub firmware

## License

UIU Underwater Robotics Team
