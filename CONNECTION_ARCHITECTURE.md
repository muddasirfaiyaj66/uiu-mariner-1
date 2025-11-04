# 🔌 CONNECTION ARCHITECTURE - UIU MARINER ROV

## 📊 System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    GROUND STATION (Windows PC)                   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              UIU MARINER GUI Application                    │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Camera 0 │  │ Camera 1 │  │ Sensors  │  │  Control │  │ │
│  │  │ Display  │  │ Display  │  │ Telemetry│  │  Panel   │  │ │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │ │
│  └───────┼─────────────┼─────────────┼─────────────┼────────┘ │
│          │             │             │             │            │
│          │ UDP:5000    │ UDP:5001    │ TCP:5002    │ TCP:7000  │
│          │             │             │             │            │
└──────────┼─────────────┼─────────────┼─────────────┼───────────┘
           │             │             │             │
           │             │             │             │
    Network │ (WiFi/      │ Ethernet) │             │
           │             │             │             │
           ▼             ▼             ▼             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    RASPBERRY PI 4 (Onboard Computer)             │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Camera 0   │  │   Camera 1   │  │  BMP388      │          │
│  │   (USB/CSI)  │  │   (USB/CSI)  │  │  Sensor      │          │
│  │              │  │              │  │  (I2C)       │          │
│  │  libcamera   │  │  libcamera   │  │              │          │
│  │  → GStreamer │  │  → GStreamer │  │  Python      │          │
│  │  → H.264     │  │  → H.264     │  │  Server      │          │
│  │  → UDP:5000  │  │  → UDP:5001  │  │  → TCP:5002  │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │               MAVProxy (MAVLink Bridge)                   │   │
│  │  Serial:/dev/ttyACM0:115200 ←→ TCP:0.0.0.0:7000         │   │
│  └────────────────────┬──────────────────────────────────────┘   │
│                       │ USB                                       │
└───────────────────────┼───────────────────────────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │   Pixhawk (Flight     │
            │   Controller)         │
            │   Running ArduSub     │
            │                       │
            │   8 ESC Outputs →     │
            │   Thruster Control    │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Electronic Speed     │
            │  Controllers (ESCs)   │
            │  × 8 Units            │
            └───────────────────────┘
                        │
                        ▼
            ┌───────────────────────┐
            │  Thrusters (Motors)   │
            │  × 8 Units            │
            │  BlueROV2 Config      │
            └───────────────────────┘
```

---

## 🔌 Port Configuration

### Ground Station → Raspberry Pi

| Service      | Port | Protocol | Direction | Purpose                 |
| ------------ | ---- | -------- | --------- | ----------------------- |
| **Camera 0** | 5000 | UDP      | ← From Pi | H.264 video stream      |
| **Camera 1** | 5001 | UDP      | ← From Pi | H.264 video stream      |
| **Sensors**  | 5002 | TCP      | ← From Pi | BMP388 telemetry (JSON) |
| **MAVLink**  | 7000 | TCP      | ← From Pi | Pixhawk commands/status |

### Raspberry Pi → Pixhawk

| Connection   | Interface    | Baudrate | Purpose               |
| ------------ | ------------ | -------- | --------------------- |
| **Pixhawk**  | /dev/ttyACM0 | 115200   | MAVLink communication |
| **BMP388**   | I2C (GPIO)   | -        | Depth/pressure sensor |
| **Camera 0** | USB/CSI      | -        | Video capture         |
| **Camera 1** | USB/CSI      | -        | Video capture         |

---

## 📡 Data Flow

### 1. Camera Stream Flow

```
Camera → libcamera-vid → GStreamer → H.264 Encoding → UDP → Ground Station → OpenCV → PyQt6 → Display
```

**Details:**

- Resolution: 640×480 @ 30fps (configurable)
- Codec: H.264 (hardware accelerated)
- Transport: UDP (low latency)
- Display: Real-time with object detection overlay

### 2. Sensor Data Flow

```
BMP388 (I2C) → Python Script → JSON Format → TCP Socket → Ground Station → GUI Update
```

**Data Format:**

```json
{
  "temperature": 25.5,
  "pressure": 1013.2,
  "depth": 5.3,
  "timestamp": "12:34:56"
}
```

### 3. Control Flow (Joystick → Thrusters)

```
Joystick Input → Pygame → Channel Mapping → MAVLink → TCP:7000 → Pi → MAVProxy → Serial → Pixhawk → RC_CHANNELS_OVERRIDE → ESCs → Thrusters
```

**Command Format:**

- 8 PWM channels (1000-2000 µs)
- 1500 = neutral
- <1500 = reverse
- > 1500 = forward

---

## 🔧 Connection States

### Fully Connected System

```
✅ Ground Station
   ├─ ✅ Camera 0: Live stream (UDP:5000)
   ├─ ✅ Camera 1: Live stream (UDP:5001)
   ├─ ✅ Sensors: Real data (TCP:5002)
   ├─ ✅ Pixhawk: Connected (TCP:7000)
   └─ ✅ Joystick: Nintendo Switch Pro Controller

✅ Raspberry Pi
   ├─ ✅ Camera 0: Streaming
   ├─ ✅ Camera 1: Streaming
   ├─ ✅ Sensor Server: Running
   ├─ ✅ MAVProxy: Bridging
   └─ ✅ Network: raspberrypi.local

✅ Pixhawk
   ├─ ✅ Serial: Connected to Pi
   ├─ ✅ Mode: MANUAL/STABILIZE
   ├─ ✅ Armed: Ready
   └─ ✅ ESCs: 8 channels responsive
```

### Current State (Mock Mode)

```
✅ Ground Station
   ├─ ⚠️ Camera 0: Placeholder shown
   ├─ ⚠️ Camera 1: Placeholder shown
   ├─ ✅ Sensors: Mock data (auto-fallback)
   ├─ ⚠️ Pixhawk: Disconnected
   └─ ✅ Joystick: Nintendo Switch Pro Controller

⚠️ Raspberry Pi
   ├─ 🔴 Not connected to network
   ├─ 🔴 Services not running
   └─ 🔴 MAVProxy not active

⚠️ Pixhawk
   └─ 🔴 No connection (requires Pi bridge)
```

---

## 🌐 Network Configuration

### Recommended Setup

#### Option 1: WiFi Direct

```
Ground Station (WiFi) ←→ Raspberry Pi (WiFi AP)
```

- Lowest latency
- Most reliable
- No router needed

#### Option 2: Local Network

```
Ground Station (WiFi) ←→ Router ←→ Raspberry Pi (Ethernet/WiFi)
```

- Easy setup
- Existing infrastructure
- Longer range

#### Option 3: Tethered (Future)

```
Ground Station ←→ Ethernet Tether ←→ Raspberry Pi
```

- Most reliable
- Longer distance
- Requires tether management

### mDNS Configuration

```
Hostname: raspberrypi.local
Fallback IP: 192.168.0.100 (static, configured)
```

---

## 🔒 Firewall Rules (Windows)

### Required Rules

```powershell
# Allow inbound UDP for camera streams
New-NetFirewallRule -DisplayName "ROV Camera 0" -Direction Inbound -LocalPort 5000 -Protocol UDP -Action Allow
New-NetFirewallRule -DisplayName "ROV Camera 1" -Direction Inbound -LocalPort 5001 -Protocol UDP -Action Allow

# Allow inbound TCP for sensors and MAVLink
New-NetFirewallRule -DisplayName "ROV Sensors" -Direction Inbound -LocalPort 5002 -Protocol TCP -Action Allow
New-NetFirewallRule -DisplayName "ROV MAVLink" -Direction Inbound -LocalPort 7000 -Protocol TCP -Action Allow

# Allow outbound connections (usually allowed by default)
New-NetFirewallRule -DisplayName "ROV Outbound" -Direction Outbound -Action Allow
```

---

## 🔍 Service Discovery

### Pi → Ground Station

```
1. Pi detects SSH client IP address
2. Broadcasts camera streams to that IP
3. Sensor/MAVLink servers listen on all interfaces (0.0.0.0)
```

### Ground Station → Pi

```
1. Uses mDNS: raspberrypi.local
2. Fallback: Scans local network (192.168.x.x)
3. Config: Manual IP if needed
```

---

## 🛠️ Testing Each Connection

### Test Camera Streams

```powershell
# Use VLC Media Player
# File → Open Network Stream
# URL: udp://@:5000  (for Camera 0)
# URL: udp://@:5001  (for Camera 1)
```

### Test Sensor Connection

```powershell
# PowerShell
Test-NetConnection -ComputerName raspberrypi.local -Port 5002

# Python test
python -c "import socket; s=socket.socket(); s.connect(('raspberrypi.local', 5002)); print(s.recv(1024))"
```

### Test MAVLink Connection

```powershell
# PowerShell
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# Using MAVProxy
mavproxy.py --master=tcp:raspberrypi.local:7000
```

---

## 📊 Bandwidth Usage

| Stream    | Bandwidth   | Notes                      |
| --------- | ----------- | -------------------------- |
| Camera 0  | ~2 Mbps     | H.264, 640×480@30fps       |
| Camera 1  | ~2 Mbps     | H.264, 640×480@30fps       |
| Sensors   | <1 Kbps     | JSON, 2 Hz update rate     |
| MAVLink   | <10 Kbps    | Binary, 10 Hz control rate |
| **Total** | **~5 Mbps** | Well within WiFi capacity  |

---

## 🎯 Connection Priorities

### Critical (Must Work)

1. **MAVLink** - Vehicle control
2. **Pixhawk** - Thruster commands
3. **Emergency Stop** - Safety

### Important (Operational)

4. **Sensors** - Depth/pressure monitoring
5. **Camera 0** - Primary vision
6. **Joystick** - Manual control

### Optional (Enhanced)

7. **Camera 1** - Secondary vision
8. **Object Detection** - AI features
9. **Telemetry Logging** - Data recording

---

## 🔄 Auto-Recovery Features

### Connection Lost Scenarios

| Lost Connection   | Behavior                      | Recovery                      |
| ----------------- | ----------------------------- | ----------------------------- |
| **Pi Network**    | Auto-fallback to mock sensors | Auto-reconnect when available |
| **Camera Stream** | Show placeholder image        | Retry on button press         |
| **Pixhawk**       | Disarm automatically          | Manual reconnect attempt      |
| **Joystick**      | Show warning, accept new      | Hot-plug supported            |

---

## 💡 Pro Tips

1. **Start Pi First** - Always power on Pi before Ground Station
2. **Check Network** - Ping before launching GUI
3. **Monitor Console** - Watch connection messages
4. **Use Mock Mode** - Test without hardware first
5. **Gradual Connection** - Connect components one at a time

---

**This diagram shows the complete connection architecture of your ROV system!** 🌊

For step-by-step connection instructions, see: `CONNECT_HARDWARE_GUIDE.md`
