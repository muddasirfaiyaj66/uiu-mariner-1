# System Architecture & Connection Guide 🎮🌊

## Overview of Complete System

Your UIU MARINER ROV system has **TWO separate computers** working together:

```
┌─────────────────────────────────────────────────────────────────┐
│                    GROUND STATION (Your PC)                      │
│  - Windows 10/11                                                 │
│  - Xbox Controller (USB/Bluetooth) ✅ CONNECTS HERE             │
│  - Runs: marinerApp.py                                           │
│  - Displays: Camera feeds, sensor data, GUI                      │
│  - Network: WiFi/Ethernet to ROV                                 │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Network (WiFi or Ethernet)
                         │ 192.168.x.x
                         │
┌────────────────────────▼────────────────────────────────────────┐
│                  ROV (Raspberry Pi + Pixhawk)                    │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐        │
│  │              Raspberry Pi 4                          │        │
│  │  - Runs: Camera streaming (GStreamer)                │        │
│  │  - Runs: Sensor data collection                      │        │
│  │  - Connected to Pixhawk via UART/USB                 │        │
│  │  - Forwards MAVLink commands to Pixhawk              │        │
│  └──────────────────────┬──────────────────────────────┘        │
│                         │                                        │
│                         │ Serial (UART/USB)                      │
│                         │ /dev/ttyUSB0:115200                    │
│                         │                                        │
│  ┌──────────────────────▼──────────────────────────────┐        │
│  │              Pixhawk (ArduSub)                       │        │
│  │  - Controls: 8 thrusters                             │        │
│  │  - Receives: RC_CHANNELS_OVERRIDE                    │        │
│  │  - Firmware: ArduSub v4.5+                           │        │
│  └──────────────────────────────────────────────────────┘        │
│                         │                                        │
│                         └─→ [Thrusters x8]                       │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🎮 Joystick Connection - YES, It's on Ground Station!

**Your question:** "my joystick will connect via bluetooth or usb in the ground station computer"

**Answer:** ✅ **CORRECT!** The Xbox controller connects to **YOUR PC** (Ground Station), not the ROV.

### How It Works:

1. **Xbox Controller → Ground Station PC**

   - Connection: USB cable **OR** Bluetooth wireless
   - Driver: Windows automatically detects Xbox controllers
   - Software: `pygame` library reads joystick input
   - Location: `src/controllers/joystickController.py` handles this

2. **Ground Station PC → ROV**
   - Your PC reads joystick
   - Converts to thruster values (PWM 1000-2000)
   - Sends MAVLink commands over network
   - ROV receives and controls thrusters

---

## Connection Methods Explained

### Ground Station → ROV Communication

**Option 1: WiFi (Most Common)**

```
Ground Station PC (WiFi) ←→ ROV Router/Access Point ←→ Raspberry Pi
IP: 192.168.0.100              IP: Router                IP: 192.168.0.104
```

**Option 2: Direct Ethernet**

```
Ground Station PC (Ethernet) ←→ Tether Cable ←→ Raspberry Pi
IP: 192.168.0.100                                 IP: 192.168.0.104
```

**Option 3: WiFi + Companion Computer**

```
Ground Station PC ←→ WiFi ←→ Companion Computer ←→ Pixhawk
                              (on ROV)
```

---

## What Runs Where?

### 🖥️ **Ground Station (Your Windows PC)**

**Hardware:**

- ✅ Xbox 360/One Controller (USB or Bluetooth)
- ✅ Monitor (displays camera feeds + GUI)
- ✅ WiFi/Ethernet adapter
- ✅ Keyboard/Mouse

**Software Running:**

- ✅ `marinerApp.py` - Main GUI application
- ✅ `cameraWorker.py` - Receives video streams
- ✅ `sensorWorker.py` - Receives sensor data
- ✅ `joystickController.py` - Reads Xbox controller
- ✅ `mavlinkConnection.py` - Sends commands to ROV

**Config (config.json):**

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "joystick_target": "xbox",
  "camera": {
    "pipeline0": "udpsrc port=5000 ...",
    "pipeline1": "udpsrc port=5001 ..."
  },
  "sensors": {
    "host": "192.168.21.126",
    "port": 5000
  }
}
```

---

### 🤖 **ROV (Raspberry Pi on Underwater Vehicle)**

**Hardware:**

- ✅ Raspberry Pi 4
- ✅ 2x Pi Cameras (front + bottom)
- ✅ Sensors (temperature, pressure, depth)
- ✅ Pixhawk flight controller
- ✅ 8x Thrusters (ESCs)

**Software Running (on Raspberry Pi):**

```python
# Camera Streaming (run on Pi)
# Stream camera 0 to port 5000
raspivid -t 0 -w 1280 -h 720 -fps 30 -b 2000000 -o - | \
  gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! \
  udpsink host=192.168.0.100 port=5000

# Stream camera 1 to port 5001
raspivid -cs 1 -t 0 -w 1280 -h 720 -fps 30 -b 2000000 -o - | \
  gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=97 ! \
  udpsink host=192.168.0.100 port=5001

# Sensor Data Server (run on Pi)
python sensor_server.py  # Sends temp/pressure/depth via TCP

# MAVLink Proxy (run on Pi)
mavproxy.py --master=/dev/ttyUSB0 --baudrate 115200 \
  --out=udpin:0.0.0.0:14550
```

**Hardware Connections on ROV:**

- Pi GPIO UART → Pixhawk TELEM2 (MAVLink)
- Pi Camera 0 → CSI Port 0
- Pi Camera 1 → CSI Port 1
- Sensors → Pi GPIO/I2C
- Pixhawk → ESCs → Thrusters

---

## Data Flow Example

### When You Move the Joystick:

```
1. [Ground Station PC]
   Xbox Controller moved
   ↓
   pygame reads joystick axes
   ↓
   joystickController.py converts to thruster values
   ↓
   mavlinkConnection.py creates RC_CHANNELS_OVERRIDE message
   ↓
   Sent over WiFi/Ethernet

2. [ROV - Raspberry Pi]
   Receives MAVLink packet on UDP:14550
   ↓
   MAVProxy forwards to Pixhawk serial port

3. [ROV - Pixhawk]
   Receives RC_CHANNELS_OVERRIDE
   ↓
   Calculates motor mixing
   ↓
   Sends PWM signals to ESCs
   ↓
   Thrusters spin!
```

---

## Xbox Controller Setup (Ground Station)

### Option 1: USB (Recommended for Reliability)

```
1. Plug Xbox controller USB cable into PC
2. Windows automatically installs drivers
3. Test: Settings → Devices → "Set up USB game controllers"
4. Run marinerApp.py - controller auto-detected
```

### Option 2: Bluetooth (Wireless)

```
1. Turn on Xbox controller (Xbox button)
2. Hold pairing button (top of controller) until flashing
3. PC: Settings → Bluetooth & Devices → Add Device
4. Select "Xbox Wireless Controller"
5. Once paired, run marinerApp.py
```

**Note:** Bluetooth has ~10-15ms more latency than USB but still perfectly fine for ROV control.

---

## Network Setup

### Ground Station PC Network Configuration

**For WiFi ROV:**

```powershell
# Set static IP (optional but recommended)
# Network Settings → WiFi → Properties → IP Settings → Manual

IP Address: 192.168.0.100
Subnet: 255.255.255.0
Gateway: 192.168.0.1
DNS: 8.8.8.8
```

**For Ethernet Tether:**

```powershell
# Network Settings → Ethernet → Properties → IP Settings → Manual

IP Address: 192.168.0.100
Subnet: 255.255.255.0
# No gateway needed for direct connection
```

### Test Connection

```powershell
# Test if you can reach ROV
ping 192.168.0.104

# Should see:
# Reply from 192.168.0.104: bytes=32 time=1ms TTL=64
```

---

## Port Scanner Usage (Ground Station vs ROV)

### ❌ **DON'T** run port scanner on Ground Station

The port scanner (`find_pixhawk.py`) is for finding **serial ports** like:

- `/dev/ttyUSB0` (Linux)
- `COM3` (Windows)

**You DON'T have serial ports to Pixhawk on Ground Station!**

### ✅ **DO** run port scanner on Raspberry Pi (ROV)

```bash
# SSH into Raspberry Pi first
ssh pi@192.168.0.104

# Then run scanner on Pi
cd /home/pi/rov-software
python find_pixhawk.py

# This finds: /dev/ttyUSB0:115200 or /dev/ttyAMA0:115200
```

### Ground Station Uses Network Connection

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550"
}
```

No scanning needed - you know the ROV's IP address!

---

## Complete Setup Checklist

### Ground Station (Your PC)

- [ ] Install Python 3.8+
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Connect Xbox controller (USB or Bluetooth)
- [ ] Set PC IP: 192.168.0.100
- [ ] Configure `config.json` with ROV IP
- [ ] Test joystick: `python -c "import pygame; pygame.init(); print(pygame.joystick.get_count())"`

### ROV (Raspberry Pi)

- [ ] Install camera streaming software
- [ ] Install sensor data server
- [ ] Install MAVProxy
- [ ] Connect Pi to Pixhawk (UART/USB)
- [ ] Run `find_pixhawk.py` to find serial port
- [ ] Configure MAVProxy with discovered port
- [ ] Start all services on boot

### Network

- [ ] Set ROV IP: 192.168.0.104
- [ ] Test ping from PC to ROV
- [ ] Verify ports open: 14550 (MAVLink), 5000 (Camera 0), 5001 (Camera 1), 5000 TCP (Sensors)

---

## Troubleshooting

### "Joystick not detected" on Ground Station

```powershell
# Check if Windows sees controller
joy.cpl

# Or use Python
python -c "import pygame; pygame.init(); j = pygame.joystick.Joystick(0); j.init(); print(j.get_name())"

# Should print: "Xbox 360 Controller" or similar
```

### "Pixhawk not connected" on Ground Station

This is **CORRECT** - your Ground Station doesn't connect directly to Pixhawk!

Your Ground Station connects to:

- ✅ ROV's Raspberry Pi via network (UDP:14550)
- ✅ Raspberry Pi connects to Pixhawk via serial

Check:

```powershell
# Can you reach the ROV?
ping 192.168.0.104

# Can you connect to MAVLink port?
Test-NetConnection -ComputerName 192.168.0.104 -Port 14550
```

---

## Summary

### ✅ What Connects Where

| Device                | Connects To       | How               | Software         |
| --------------------- | ----------------- | ----------------- | ---------------- |
| **Xbox Controller**   | Ground Station PC | USB/Bluetooth     | pygame           |
| **Ground Station PC** | Raspberry Pi      | WiFi/Ethernet     | MAVLink over UDP |
| **Raspberry Pi**      | Pixhawk           | Serial (UART/USB) | MAVProxy         |
| **Pixhawk**           | Thrusters         | PWM wires         | ArduSub          |

### 🎮 Your Joystick Setup is CORRECT!

**YES**, your Xbox controller connects to your **Ground Station PC** via:

- ✅ USB cable (plug and play)
- ✅ Bluetooth wireless (pair in Windows settings)

**NO**, joystick does NOT connect to:

- ❌ ROV
- ❌ Raspberry Pi
- ❌ Pixhawk

The Ground Station reads the joystick and sends commands over the network to the ROV!

---

_Architecture Guide v1.0_  
_UIU MARINER ROV Control System_
