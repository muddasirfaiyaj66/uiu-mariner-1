# 🚀 REAL HARDWARE DEPLOYMENT GUIDE

## ✅ All Mock Data REMOVED!

This system now uses **REAL HARDWARE ONLY**. All fake/mock data has been removed and replaced with tested production code from your repository.

---

## 📋 What Changed

### ❌ Removed (Mock/Fake Data)

- ✅ Mock sensor worker with fake temperature/pressure/depth
- ✅ Test pattern camera feeds (videotestsrc)
- ✅ Hard-coded IP addresses
- ✅ Placeholder values

### ✅ Added (Real Hardware)

- ✅ Real BMP388 sensor reading (I2C on Raspberry Pi)
- ✅ Real H.264 camera streaming (libcamera + GStreamer)
- ✅ Real MAVProxy TCP socket communication
- ✅ Tested joystick axis mappings from control.py
- ✅ Production-ready Raspberry Pi scripts

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   GROUND STATION PC (Windows)                │
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  Controller  │──────▶│ marinerApp.py│                     │
│  │ (Switch/Xbox)│      │              │                     │
│  └──────────────┘      │  - Joystick  │                     │
│                        │  - GUI       │                     │
│                        │  - MAVLink   │                     │
│                        │  - Cameras   │                     │
│                        │  - Sensors   │                     │
│                        └──────────────┘                     │
│                               │                               │
└───────────────────────────────┼───────────────────────────────┘
                                │
                          Network (Ethernet/WiFi)
                                │
┌───────────────────────────────┼───────────────────────────────┐
│                   RASPBERRY PI (ROV)                          │
│                               │                               │
│  ┌────────────────────────────┴──────────────────────────┐   │
│  │                  Python Scripts                       │   │
│  │                                                        │   │
│  │  ┌──────────────────┐  ┌──────────────────┐         │   │
│  │  │ pi_sensor_server │  │ pi_mavproxy_server│         │   │
│  │  │ (TCP:5000)       │  │ (TCP:7000)       │         │   │
│  │  │                  │  │                  │         │   │
│  │  │ BMP388 Sensor ───┤  │ MAVProxy       │         │   │
│  │  │ (I2C)            │  │   │             │         │   │
│  │  └──────────────────┘  └───┼─────────────┘         │   │
│  │                             │                        │   │
│  │  ┌──────────────────┐  ┌───┴─────────────┐         │   │
│  │  │ ./cam0.sh        │  │   /dev/serial0  │         │   │
│  │  │ (UDP:5000)       │  │   (UART)        │         │   │
│  │  │                  │  └─────────────────┘         │   │
│  │  │ Camera 0 ────────┤          │                    │   │
│  │  │ (libcamera)      │          ▼                    │   │
│  │  └──────────────────┘    ┌──────────┐              │   │
│  │                          │ Pixhawk  │              │   │
│  │  ┌──────────────────┐    │ (ArduSub)│              │   │
│  │  │ ./cam1.sh        │    │          │              │   │
│  │  │ (UDP:5001)       │    │ 8 ESCs   │              │   │
│  │  │                  │    │          │              │   │
│  │  │ Camera 1 ────────┤    └────┬─────┘              │   │
│  │  │ (libcamera)      │         │                    │   │
│  │  └──────────────────┘         │                    │   │
│  └────────────────────────────────┼────────────────────┘   │
│                                   │                        │
│                              8 Thrusters                   │
└────────────────────────────────────────────────────────────┘
```

---

## 🔧 Hardware Requirements

### Raspberry Pi (ROV)

- ✅ Raspberry Pi 4 (tested model)
- ✅ 2x Raspberry Pi Cameras
- ✅ BMP388 Pressure/Temperature sensor (I2C)
- ✅ Pixhawk flight controller (ArduSub)
- ✅ 8x ESCs + Thrusters
- ✅ Ethernet connection to Ground Station

### Ground Station PC

- ✅ Windows 10/11
- ✅ GStreamer installed (for camera feeds)
- ✅ Game controller (Xbox/Switch/PlayStation)
- ✅ Python 3.8+ with virtual environment
- ✅ Network connection to Raspberry Pi

---

## 📶 Network Configuration

### IP Addresses

| Device                | IP Address     | Ports                                                                |
| --------------------- | -------------- | -------------------------------------------------------------------- |
| **Ground Station PC** | 192.168.0.100  | -                                                                    |
| **Raspberry Pi**      | 192.168.21.126 | TCP:5000 (sensors)<br>TCP:7000 (MAVProxy)<br>UDP:5000/5001 (cameras) |

### config.json Settings

```json
{
  "mavlink_connection": "tcp:192.168.21.126:7000",
  "sensors": {
    "host": "192.168.21.126",
    "port": 5000,
    "protocol": "tcp",
    "mock_mode": false
  },
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  }
}
```

---

## 🚀 Deployment Steps

### Part 1: Raspberry Pi Setup

#### 1. Copy Scripts to Pi

```bash
# From Ground Station
scp -r pi_scripts pi@192.168.21.126:~/mariner/
```

#### 2. SSH to Raspberry Pi

```bash
ssh pi@192.168.21.126
```

#### 3. Install Dependencies

```bash
cd ~/mariner/pi_scripts

# System packages
sudo apt-get update
sudo apt-get install -y python3-pip python3-smbus gstreamer1.0-tools libcamera-apps

# Python packages
sudo pip3 install pymavlink

# Enable I2C
sudo raspi-config
# → Interface Options → I2C → Enable

# Enable UART
sudo raspi-config
# → Interface Options → Serial Port
# → Login shell: NO
# → Serial hardware: YES

# Add user to groups
sudo usermod -a -G i2c,dialout pi

# Reboot
sudo reboot
```

#### 4. Test Hardware

```bash
# Test I2C sensor
sudo i2cdetect -y 0
# Should show 0x77

# Test cameras
libcamera-hello --list-cameras
# Should show 2 cameras

# Test serial
ls -l /dev/serial0
# Should exist

# Test MAVProxy
mavproxy.py --version
```

#### 5. Make Scripts Executable

```bash
cd ~/mariner/pi_scripts
chmod +x *.sh
```

#### 6. Start Services

**Option A: Manual (for testing)**

```bash
# Terminal 1: Sensors
python3 pi_sensor_server.py

# Terminal 2: MAVProxy
python3 pi_mavproxy_server.py

# Terminal 3: Camera 0
./cam0.sh 192.168.0.100

# Terminal 4: Camera 1
./cam1.sh 192.168.0.100
```

**Option B: Screen Sessions (recommended)**

```bash
# Start all services in background
screen -dmS sensors python3 pi_sensor_server.py
screen -dmS mavproxy python3 pi_mavproxy_server.py
screen -dmS cam0 ./cam0.sh 192.168.0.100
screen -dmS cam1 ./cam1.sh 192.168.0.100

# Check they're running
screen -ls

# View a session
screen -r sensors  # Ctrl+A, D to detach
```

---

### Part 2: Ground Station Setup

#### 1. Install GStreamer (Windows)

Download from: https://gstreamer.freedesktop.org/download/

Install both:

- `gstreamer-1.0-msvc-x86_64-XXX.msi` (runtime)
- `gstreamer-1.0-devel-msvc-x86_64-XXX.msi` (development)

Add to PATH:

```
C:\gstreamer\1.0\msvc_x86_64\bin
```

Verify:

```powershell
gst-inspect-1.0 --version
```

#### 2. Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

#### 3. Verify Configuration

```powershell
python system_check.py
```

Should show:

```
✅ Python Version
✅ Virtual Environment
✅ Dependencies
✅ Configuration
✅ Joystick/Controller
✅ UI Files
```

#### 4. Connect Controller

Plug in your Xbox/Switch/PlayStation controller via USB or Bluetooth.

Test it:

```powershell
python test_joystick.py
```

#### 5. Test Network Connectivity

```powershell
ping 192.168.21.126
```

Should get replies.

---

## 🎮 Running the System

### 1. Start Raspberry Pi Services

On the Pi (SSH):

```bash
cd ~/mariner/pi_scripts
screen -dmS sensors python3 pi_sensor_server.py
screen -dmS mavproxy python3 pi_mavproxy_server.py
screen -dmS cam0 ./cam0.sh 192.168.0.100
screen -dmS cam1 ./cam1.sh 192.168.0.100
```

Verify:

```bash
screen -ls
# Should show 4 sessions

netstat -an | grep -E "5000|5001|7000"
# Should show LISTEN on these ports
```

### 2. Start Ground Station Application

On Windows:

```powershell
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

You should see:

```
✅ Running in virtual environment
✅ All dependencies installed

[JOYSTICK] Found 1 joystick(s)
[JOYSTICK] ✅ Connected to: Nintendo Switch Pro Controller
[PIXHAWK] ✅ Connected
[SENSORS] ✅ TCP connection established
[CAMERAS] ✅ Dual camera feeds started
[MARINER] ✅ Application initialized successfully
```

---

## 🔍 Verification Checklist

### Raspberry Pi

- [ ] All 4 screen sessions running (`screen -ls`)
- [ ] Sensor server shows "Server listening on 0.0.0.0:5000"
- [ ] MAVProxy server shows "Listening on 0.0.0.0:7000"
- [ ] Camera 0 streaming (no errors in cam0 session)
- [ ] Camera 1 streaming (no errors in cam1 session)
- [ ] Pixhawk connected to /dev/serial0
- [ ] BMP388 sensor detected on I2C bus

### Ground Station

- [ ] Controller detected and ready
- [ ] Pixhawk connection established
- [ ] Sensor data updating (temperature, pressure, depth)
- [ ] Camera feeds showing live video
- [ ] GUI responsive
- [ ] Control loop running (10 Hz)

---

## ⚠️ Safety Checklist

Before operating thrusters:

- [ ] ROV in water (thrusters must be submerged!)
- [ ] Tether secure and untangled
- [ ] Emergency stop button accessible
- [ ] All systems showing "Connected"
- [ ] Controller responding to input
- [ ] Team members ready
- [ ] Clear of obstacles
- [ ] Tested with thrusters DISARMED first

---

## 🐛 Troubleshooting

### No Sensor Data

**Check Pi:**

```bash
# Is sensor server running?
screen -r sensors

# Check I2C
sudo i2cdetect -y 0

# Manual test
python3 -c "import smbus; bus=smbus.SMBus(0); print(bus.read_byte_data(0x77, 0x00))"
```

**Check Ground Station:**

```bash
# Can you reach the Pi?
ping 192.168.21.126

# Is port open?
telnet 192.168.21.126 5000
```

### No Camera Feeds

**Check Pi:**

```bash
# Are cameras detected?
libcamera-hello --list-cameras

# Are streams running?
screen -r cam0
screen -r cam1

# Check GStreamer
gst-inspect-1.0 --version
```

**Check Ground Station:**

```bash
# Is GStreamer installed?
gst-inspect-1.0 --version

# Test UDP reception
gst-launch-1.0 udpsrc port=5000 ! fakesink
```

### No Pixhawk Connection

**Check Pi:**

```bash
# Is MAVProxy running?
screen -r mavproxy

# Check serial device
ls -l /dev/serial0

# Test MAVProxy manually
mavproxy.py --master=/dev/serial0 --baudrate=57600
```

**Check Ground Station:**

```bash
# Can you reach MAVProxy port?
telnet 192.168.21.126 7000
```

---

## 📚 Documentation

- **README_PI_SCRIPTS.md** - Raspberry Pi scripts documentation
- **CONTROLLER_READY.md** - Controller setup guide
- **GSTREAMER_GUIDE.md** - GStreamer installation (Windows)
- **TROUBLESHOOTING.md** - Complete troubleshooting guide
- **README_COMPLETE.md** - Full system documentation

---

## ✅ What You Have Now

✅ **NO MOCK DATA** - Everything uses real hardware  
✅ **Tested Scripts** - All Pi scripts from your working repository  
✅ **Real Sensors** - BMP388 via I2C  
✅ **Real Cameras** - H.264 streaming via libcamera + GStreamer  
✅ **Real MAVLink** - TCP socket to MAVProxy  
✅ **Real Joystick** - Tested axis mappings from control.py  
✅ **Production Ready** - Ready for actual ROV deployment

---

**Last Updated:** November 4, 2025  
**Status:** 🚀 PRODUCTION READY - ALL MOCK DATA REMOVED
