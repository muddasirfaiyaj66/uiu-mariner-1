# Raspberry Pi Scripts - UIU MARINER ROV

## 📁 Overview

These scripts run on the **Raspberry Pi** inside the ROV. They handle:

- 📹 Camera streaming (H.264 via UDP/RTP)
- 📊 Sensor data transmission (BMP388 via TCP)
- 🎮 MAVProxy server for Pixhawk control (TCP socket interface)

## 🚀 Quick Start

### 1. Copy Files to Raspberry Pi

```bash
# On your computer
scp -r pi_scripts pi@192.168.21.126:~/mariner/
```

### 2. Install Dependencies on Pi

```bash
ssh pi@192.168.21.126
cd ~/mariner/pi_scripts
sudo apt-get update
sudo apt-get install -y python3-smbus gstreamer1.0-tools libcamera-apps
sudo pip3 install pymavlink
chmod +x *.sh
```

### 3. Start All Services

**Option A: Start Individually**

```bash
# Terminal 1: Sensor server
python3 pi_sensor_server.py --host 0.0.0.0 --port 5000

# Terminal 2: MAVProxy server
python3 pi_mavproxy_server.py --master /dev/serial0 --baudrate 57600 --port 7000

# Terminal 3: Camera 0
./cam0.sh 192.168.0.100

# Terminal 4: Camera 1
./cam1.sh 192.168.0.100
```

**Option B: Use Screen Sessions**

```bash
# Create screen sessions
screen -dmS sensors python3 pi_sensor_server.py
screen -dmS mavproxy python3 pi_mavproxy_server.py
screen -dmS cam0 ./cam0.sh 192.168.0.100
screen -dmS cam1 ./cam1.sh 192.168.0.100

# List sessions
screen -ls

# Attach to a session
screen -r sensors
```

---

## 📹 Camera Scripts

### pi_camera_server.py

Streams H.264 video from Raspberry Pi cameras via UDP/RTP.

**Usage:**

```bash
python3 pi_camera_server.py <camera_id> <dest_ip> <port> [options]
```

**Arguments:**

- `camera_id`: Camera index (0 or 1)
- `dest_ip`: Ground Station IP address
- `port`: UDP port number
- `--payload`: RTP payload type (default: 96)
- `--width`: Video width (default: 640)
- `--height`: Video height (default: 480)
- `--framerate`: FPS (default: 30)

**Examples:**

```bash
# Camera 0 → 192.168.0.100:5000
python3 pi_camera_server.py 0 192.168.0.100 5000 --payload 96

# Camera 1 → 192.168.0.100:5001 (higher resolution)
python3 pi_camera_server.py 1 192.168.0.100 5001 --payload 97 --width 1280 --height 720
```

### cam0.sh / cam1.sh

Convenience scripts for starting cameras.

**Usage:**

```bash
./cam0.sh [GROUND_STATION_IP]
./cam1.sh [GROUND_STATION_IP]
```

**Examples:**

```bash
# Use default IP (192.168.0.100)
./cam0.sh

# Specify custom IP
./cam0.sh 10.42.0.1
```

---

## 📊 Sensor Script

### pi_sensor_server.py

Reads BMP388 pressure/temperature/depth sensor via I2C and sends data to Ground Station via TCP.

**Usage:**

```bash
python3 pi_sensor_server.py [options]
```

**Arguments:**

- `--host`: Bind address (default: 0.0.0.0)
- `--port`: TCP port (default: 5000)

**Examples:**

```bash
# Standard usage
python3 pi_sensor_server.py

# Custom port
python3 pi_sensor_server.py --port 8000
```

**Data Format:**

```
temperature,pressure,depth\n
```

Example: `25.3,1015.2,3.5\n`

**I2C Setup:**

Enable I2C on Raspberry Pi:

```bash
sudo raspi-config
# → Interface Options → I2C → Enable
sudo reboot
```

Check I2C device:

```bash
sudo i2cdetect -y 0  # or -y 1 depending on your Pi model
```

You should see `0x77` (BMP388 address).

---

## 🎮 MAVProxy Script

### pi_mavproxy_server.py

Provides TCP socket interface to MAVProxy for Pixhawk control.

**Usage:**

```bash
python3 pi_mavproxy_server.py [options]
```

**Arguments:**

- `--master`: MAVLink serial device (default: /dev/serial0)
- `--baudrate`: Serial baud rate (default: 57600)
- `--host`: Server bind address (default: 0.0.0.0)
- `--port`: TCP server port (default: 7000)

**Examples:**

```bash
# Standard usage
python3 pi_mavproxy_server.py

# USB Pixhawk connection
python3 pi_mavproxy_server.py --master /dev/ttyACM0 --baudrate 115200

# Custom port
python3 pi_mavproxy_server.py --port 5760
```

**Serial Port Setup:**

Enable UART on Raspberry Pi:

```bash
sudo raspi-config
# → Interface Options → Serial Port
# → "Would you like a login shell accessible over serial?" → NO
# → "Would you like serial port hardware enabled?" → YES
sudo reboot
```

Test serial connection:

```bash
ls -l /dev/serial*
# Should show /dev/serial0
```

---

## 🔧 Troubleshooting

### Camera Not Working

**Check libcamera:**

```bash
libcamera-hello --list-cameras
```

**Check GStreamer:**

```bash
gst-inspect-1.0 --version
gst-inspect-1.0 rtph264pay
```

**Test camera directly:**

```bash
libcamera-vid --camera 0 -t 5000 -o test.h264
```

### Sensor Not Working

**Check I2C:**

```bash
sudo i2cdetect -y 0
```

**Check permissions:**

```bash
sudo usermod -a -G i2c pi
sudo reboot
```

**Test sensor:**

```python
import smbus
bus = smbus.SMBus(0)
data = bus.read_byte_data(0x77, 0x00)
print(f"Sensor ID: {hex(data)}")
```

### MAVProxy Not Working

**Check serial device:**

```bash
ls -l /dev/serial0 /dev/ttyACM0
```

**Test MAVProxy manually:**

```bash
mavproxy.py --master=/dev/serial0 --baudrate=57600
```

**Check permissions:**

```bash
sudo usermod -a -G dialout pi
sudo reboot
```

---

## 🌐 Network Configuration

### Recommended Setup

| Device            | IP Address      | Purpose             |
| ----------------- | --------------- | ------------------- |
| Ground Station PC | 192.168.0.100   | Control application |
| Raspberry Pi      | 192.168.21.126  | ROV computer        |
| Pixhawk           | Connected to Pi | Flight controller   |

### Update config.json on Ground Station

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

## 🔐 Auto-Start on Boot

Create systemd service files:

**1. Sensor Service:**

```bash
sudo nano /etc/systemd/system/mariner-sensors.service
```

```ini
[Unit]
Description=Mariner ROV Sensor Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/mariner/pi_scripts/pi_sensor_server.py
WorkingDirectory=/home/pi/mariner/pi_scripts
User=root
Restart=always

[Install]
WantedBy=multi-user.target
```

**2. MAVProxy Service:**

```bash
sudo nano /etc/systemd/system/mariner-mavproxy.service
```

```ini
[Unit]
Description=Mariner ROV MAVProxy Server
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/mariner/pi_scripts/pi_mavproxy_server.py
WorkingDirectory=/home/pi/mariner/pi_scripts
User=pi
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable services:**

```bash
sudo systemctl enable mariner-sensors.service
sudo systemctl enable mariner-mavproxy.service
sudo systemctl start mariner-sensors.service
sudo systemctl start mariner-mavproxy.service
```

**Check status:**

```bash
sudo systemctl status mariner-sensors.service
sudo systemctl status mariner-mavproxy.service
```

---

## 📋 Testing Checklist

### Before Deployment

- [ ] All scripts executable (`chmod +x *.sh`)
- [ ] I2C enabled and BMP388 detected
- [ ] UART enabled for serial communication
- [ ] Both cameras detected (`libcamera-hello --list-cameras`)
- [ ] GStreamer installed and working
- [ ] MAVProxy installed (`mavproxy.py --version`)
- [ ] Network connectivity tested (`ping 192.168.0.100`)
- [ ] Correct IP addresses in Ground Station config.json

### Startup Test

```bash
# 1. Start sensor server
python3 pi_sensor_server.py &

# 2. Check connection
netstat -an | grep 5000

# 3. Start MAVProxy
python3 pi_mavproxy_server.py &

# 4. Check connection
netstat -an | grep 7000

# 5. Start cameras
./cam0.sh 192.168.0.100 &
./cam1.sh 192.168.0.100 &

# 6. Check processes
ps aux | grep python3
```

---

## 📚 Related Documentation

- **README_COMPLETE.md** - Main system documentation
- **SYSTEM_OVERVIEW.md** - Architecture overview
- **GSTREAMER_GUIDE.md** - Camera streaming setup (Ground Station)
- **CONTROLLER_READY.md** - Joystick setup (Ground Station)

---

**Last Updated:** November 4, 2025  
**Based on:** Tested code from Autonomous-Underwater-Vehicle---Team-UIU-H.Y.D.RA repository
