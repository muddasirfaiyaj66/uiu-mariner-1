# UIU MARINER - ROV Control System

## 🌊 Overview

Complete software solution for controlling an underwater ROV (Remotely Operated Vehicle) using:

- **Hardware**: Pixhawk flight controller running ArduSub firmware
- **Communication**: MAVLink protocol over UDP/TCP/Serial
- **Input**: Xbox 360 / compatible gamepad
- **Interface**: PyQt6 desktop application

## 🏗️ System Architecture

```
┌─────────────────┐
│   PC Software   │
│  (This Repo)    │
├─────────────────┤
│ • PyQt6 GUI     │
│ • Joystick      │
│ • MAVLink       │
└────────┬────────┘
         │ Ethernet UDP
         │ 192.168.0.104:14550
┌────────▼────────┐
│  Raspberry Pi   │
│   (Optional)    │
└────────┬────────┘
         │ UART/TELEM2
┌────────▼────────┐
│    Pixhawk      │
│  ArduSub v4.5+  │
└────────┬────────┘
         │ PWM Signals
┌────────▼────────┐
│  8x Thrusters   │
│   + ESCs        │
└─────────────────┘
```

## 📦 Installation

### 1. Prerequisites

- **Python 3.8+** (3.10 recommended)
- **Xbox 360 Controller** or compatible gamepad
- **Pixhawk** running ArduSub firmware (v4.5.6 or later)
- **Network connection** to Pixhawk/Raspberry Pi

### 2. Install Dependencies

```powershell
# Clone or navigate to this directory
cd "e:\UIU MARINER\mariner-software-1.0"

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install required packages
pip install -r requirements.txt
```

### 3. Configure Connection

Edit `config.json`:

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "joystick_target": "xbox",
  "update_rate_hz": 10
}
```

**Connection String Examples:**

- UDP: `"udp:192.168.0.104:14550"` (default)
- TCP: `"tcp:10.42.0.185:5760"`
- Serial: `"serial:/dev/ttyUSB0:57600"` (Linux) or `"serial:COM3:57600"` (Windows)

## 🚀 Usage

### Launch Application

```powershell
# From project root
python src/ui/rovControlApp.py
```

Or use the launcher script:

```powershell
.\launch.ps1
```

### Control Layout (Xbox 360)

**Left Stick:**

- **Y-Axis**: Forward/Backward (Thrusters 1, 8)
- **X-Axis**: Left/Right Rotation (Thrusters 2, 5)

**Right Stick:**

- **Y-Axis**: Up/Down (Thrusters 3, 4, 6, 7)

**Buttons:**

- **Start**: Emergency Stop (all thrusters to neutral)
- **Back**: Reserved
- **A/B/X/Y**: Reserved for future features

### GUI Controls

1. **Connect**: Click "Reconnect Pixhawk" if connection fails
2. **Set Mode**: Choose MANUAL or STABILIZE mode
3. **Arm**: Click "ARM THRUSTERS" (thrusters will remain at neutral until joystick input)
4. **Control**: Use joystick to pilot ROV
5. **Emergency**: Click "EMERGENCY STOP" or press Start button to immediately stop all thrusters

## 🔧 Configuration

### Thruster Channel Mapping

Current configuration (ArduSub standard frame):

| Channel | Function         | Thruster Position |
| ------- | ---------------- | ----------------- |
| 1       | Forward/Backward | Left Front        |
| 2       | Left/Right Yaw   | Right Lateral     |
| 3       | Up/Down          | Front Vertical    |
| 4       | Up/Down          | Rear Vertical     |
| 5       | Left/Right Yaw   | Left Lateral      |
| 6       | Up/Down          | Front Vertical    |
| 7       | Up/Down          | Rear Vertical     |
| 8       | Forward/Backward | Right Front       |

**Note**: If your thruster configuration differs, modify `compute_thruster_channels()` in `src/controllers/joystickController.py`.

### Network Setup

**Direct Connection (PC ↔ Pixhawk):**

1. Connect Pixhawk USB to PC
2. Check COM port in Device Manager
3. Use `"serial:COM3:57600"` in config.json

**Via Raspberry Pi:**

1. Connect PC and Pi to same network
2. Configure Pi as MAVLink router (see `docs/pi-setup.md`)
3. Use `"udp:<PI_IP>:14550"` in config.json

## 📁 Project Structure

```
mariner-software-1.0/
├── src/
│   ├── connections/
│   │   └── mavlinkConnection.py    # MAVLink communication
│   ├── controllers/
│   │   └── joystickController.py   # Joystick input processing
│   ├── ui/
│   │   └── rovControlApp.py        # Main GUI application
│   └── resources/                  # Images, icons (future)
├── media/
│   ├── images/
│   └── videos/
├── config.json                     # Configuration file
├── requirements.txt                # Python dependencies
├── launch.ps1                      # Windows launcher script
├── launch.sh                       # Linux launcher script
└── README.md                       # This file
```

## 🛠️ Troubleshooting

### "No joystick detected"

- Ensure controller is plugged in via USB
- Press Xbox button to power on
- Check Windows Game Controllers settings

### "Connection failed"

- Verify IP address and port in `config.json`
- Ensure Pixhawk/Pi is powered on and connected to network
- Check firewall settings (allow UDP port 14550)
- Test with QGroundControl to verify MAVLink connection

### "Cannot arm"

- Ensure Pixhawk is receiving valid MAVLink heartbeat
- Check ArduSub pre-arm checks in QGroundControl
- Verify ArduSub firmware version (4.5.6+)

### Thrusters not responding

- Confirm vehicle is ARMED (status shows "Armed: YES")
- Check ESC calibration in QGroundControl
- Verify thruster channel mapping matches your physical setup
- Ensure joystick axes are moving (check "Joystick Input" panel)

## 🧪 Testing Without Hardware

To test joystick input without connecting to Pixhawk:

1. Comment out `self.connect_pixhawk()` in `rovControlApp.py` (line ~42)
2. Run application
3. Move joystick and observe thruster values update in GUI

## 🔐 Safety Features

- **Emergency Stop**: Immediately disarms and neutralizes all thrusters
- **Arm Guard**: Thrusters cannot activate without explicit arming
- **Dead Zone**: Small joystick movements ignored (±3%)
- **Value Clamping**: All PWM values clamped to 1000-2000 range
- **Connection Monitoring**: Control disabled if Pixhawk disconnects

## 📚 Additional Resources

- [ArduSub Documentation](https://www.ardusub.com/)
- [MAVLink Protocol](https://mavlink.io/en/)
- [Pygame Documentation](https://www.pygame.org/docs/)
- [PyQt6 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt6/)

## 🤝 Team UIU HYDRA

Developed for the UIU MARINER autonomous underwater vehicle project.

**Version**: 1.0  
**Last Updated**: November 2025  
**License**: MIT

---

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Xbox controller connected
- [ ] `config.json` configured with correct IP/port
- [ ] Pixhawk powered on and connected
- [ ] ArduSub firmware v4.5.6+ installed
- [ ] Run `python src/ui/rovControlApp.py`
- [ ] Verify Pixhawk connection (green status)
- [ ] Set mode to MANUAL
- [ ] ARM thrusters
- [ ] Test joystick control
- [ ] Emergency stop accessible!

**Happy Diving! 🌊🤖**
