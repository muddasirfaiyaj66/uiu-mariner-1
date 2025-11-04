# 🍓 Raspberry Pi Setup Guide - Complete Instructions

## Your Raspberry Pi Information

- **Hostname:** raspberrypi.local
- **Username:** pi
- **Password:** 1234

---

## 📋 Step 1: Connect to Your Raspberry Pi

From your Windows PC, open PowerShell and connect via SSH:

```powershell
ssh pi@raspberrypi.local
# Password: 1234
```

---

## 📦 Step 2: Install Required Packages

Once connected to the Pi, run these commands:

```bash
# Update package list
sudo apt-get update

# Install Python dependencies
sudo apt-get install -y python3-pip python3-smbus

# Install camera tools
sudo apt-get install -y libcamera-apps gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad

# Install Python packages
pip3 install pymavlink --break-system-packages

# Install screen for background processes
sudo apt-get install -y screen
```

---

## 🔧 Step 3: Enable Hardware Interfaces

Enable I2C (for BMP388 sensor) and UART (for Pixhawk):

```bash
sudo raspi-config
```

Navigate to:

1. **Interface Options** → **I2C** → **Enable**
2. **Interface Options** → **Serial Port** →
   - "Login shell over serial?" → **No**
   - "Serial port hardware enabled?" → **Yes**
3. **Finish** → **Reboot**

After reboot, verify:

```bash
ls /dev/i2c* /dev/serial0
# Should show: /dev/i2c-0 /dev/i2c-1 /dev/serial0
```

---

## 📂 Step 4: Copy Scripts to Raspberry Pi

From your **Windows PC PowerShell**, copy the pi_scripts folder:

```powershell
# Navigate to your project folder
cd "E:\UIU MARINER\mariner-software-1.0"

# Copy entire pi_scripts folder to Pi
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
# Password: 1234
```

---

## 🎬 Step 5: Make Scripts Executable

Back on the **Raspberry Pi SSH session**:

```bash
cd ~/mariner/pi_scripts
chmod +x *.sh
chmod +x *.py
```

---

## 🚀 Step 6: Start All Services

### Option A: Start Everything with One Command

```bash
cd ~/mariner/pi_scripts
./start_all_services.sh
```

### Option B: Start Services Individually

**1. Sensor Server (BMP388)**

```bash
screen -dmS sensors python3 ~/mariner/pi_scripts/pi_sensor_server.py
```

**2. MAVProxy Server (Pixhawk Communication)**

```bash
screen -dmS mavproxy python3 ~/mariner/pi_scripts/pi_mavproxy_server.py --master /dev/serial0 --baudrate 57600 --port 7000
```

**3. Camera 0 Stream**

```bash
# Get your Ground Station IP first (from Windows: ipconfig)
# Replace YOUR_GROUND_STATION_IP with actual IP (e.g., 192.168.1.100)
screen -dmS cam0 ~/mariner/pi_scripts/cam0.sh YOUR_GROUND_STATION_IP
```

**4. Camera 1 Stream**

```bash
screen -dmS cam1 ~/mariner/pi_scripts/cam1.sh YOUR_GROUND_STATION_IP
```

---

## 🔍 Step 7: Check Service Status

View running services:

```bash
screen -ls
# Should show: sensors, mavproxy, cam0, cam1
```

Attach to a service to see its output:

```bash
screen -r sensors    # View sensor server output
# Press Ctrl+A then D to detach (leave running)

screen -r mavproxy   # View MAVProxy output
screen -r cam0       # View camera 0 output
screen -r cam1       # View camera 1 output
```

Stop a service:

```bash
screen -X -S sensors quit   # Stop sensor server
screen -X -S mavproxy quit  # Stop MAVProxy
screen -X -S cam0 quit      # Stop camera 0
screen -X -S cam1 quit      # Stop camera 1
```

---

## 🧪 Step 8: Test Individual Components

### Test BMP388 Sensor

```bash
python3 ~/mariner/pi_scripts/test_bmp388.py
# Should show: Temperature, Pressure, Altitude readings
```

### Test Pixhawk Connection

```bash
python3 -m pymavlink.mavproxy --master=/dev/serial0 --baudrate=57600
# Should show: MAVLink messages from Pixhawk
# Press Ctrl+C to exit
```

### Test Camera 0

```bash
libcamera-hello --camera 0 -t 5000
# Should show 5 second preview from camera 0
```

### Test Camera 1

```bash
libcamera-hello --camera 1 -t 5000
# Should show 5 second preview from camera 1
```

---

## 🖥️ Step 9: Find Your Ground Station IP

On your **Windows PC PowerShell**:

```powershell
ipconfig
# Look for "IPv4 Address" under your active network adapter
# Example: 192.168.1.100
```

Update camera scripts with this IP:

```bash
# On Raspberry Pi
cd ~/mariner/pi_scripts
nano cam0.sh
# Change: GROUND_STATION_IP="192.168.1.100"
# Press Ctrl+X, Y, Enter to save

nano cam1.sh
# Change: GROUND_STATION_IP="192.168.1.100"
# Press Ctrl+X, Y, Enter to save
```

---

## ✅ Step 10: Verify Everything is Running

From **Raspberry Pi**, check all services:

```bash
# 1. Check sensor server
curl localhost:5000
# Should connect and show waiting for data

# 2. Check MAVProxy
ps aux | grep mavproxy
# Should show running process

# 3. Check cameras
screen -ls
# Should list: cam0, cam1, sensors, mavproxy
```

From **Windows PC PowerShell**, test connectivity:

```powershell
# Test Pi is reachable
ping raspberrypi.local

# Test sensor port
Test-NetConnection raspberrypi.local -Port 5000

# Test MAVProxy port
Test-NetConnection raspberrypi.local -Port 7000
```

---

## 🚀 Step 11: Launch Ground Station Application

On your **Windows PC**:

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

You should now see:

- ✅ Pixhawk connected
- ✅ Sensors connected (depth, temp, pressure updating)
- ✅ Camera feeds showing live video
- ✅ Nintendo Switch Pro Controller connected

---

## 🔧 Troubleshooting

### Sensors Not Working

```bash
# Check I2C devices
sudo i2cdetect -y 1
# Should show device at address 0x77 (BMP388)

# Check sensor server logs
screen -r sensors
```

### Pixhawk Not Connecting

```bash
# Check serial connection
ls -l /dev/serial0
# Should show: /dev/serial0 -> ttyAMA0

# Test raw serial data
cat /dev/serial0
# Should show binary data (MAVLink packets)

# Check MAVProxy logs
screen -r mavproxy
```

### Cameras Not Streaming

```bash
# List available cameras
libcamera-hello --list-cameras
# Should show: 0: imx219 or similar

# Check camera logs
screen -r cam0
screen -r cam1

# Verify Ground Station IP is correct in cam0.sh and cam1.sh
cat ~/mariner/pi_scripts/cam0.sh | grep GROUND_STATION_IP
```

### Network Issues

```bash
# Check Pi IP address
hostname -I

# Check if services are listening
sudo netstat -tulpn | grep LISTEN
# Should show ports 5000 (sensors) and 7000 (MAVProxy)
```

---

## 🔄 Auto-Start Services on Boot (Optional)

To make services start automatically when Pi boots:

```bash
# Create startup script
sudo nano /etc/rc.local

# Add before "exit 0":
su - pi -c "cd /home/pi/mariner/pi_scripts && ./start_all_services.sh"

# Save and exit (Ctrl+X, Y, Enter)

# Test by rebooting
sudo reboot
```

---

## 📊 Service Summary

| Service           | Purpose          | Port       | Command                                              |
| ----------------- | ---------------- | ---------- | ---------------------------------------------------- |
| **Sensor Server** | BMP388 data      | 5000       | `screen -dmS sensors python3 pi_sensor_server.py`    |
| **MAVProxy**      | Pixhawk comms    | 7000       | `screen -dmS mavproxy python3 pi_mavproxy_server.py` |
| **Camera 0**      | Front camera     | 5000 (UDP) | `screen -dmS cam0 ./cam0.sh GROUND_IP`               |
| **Camera 1**      | Secondary camera | 5001 (UDP) | `screen -dmS cam1 ./cam1.sh GROUND_IP`               |

---

## 🎯 Quick Command Reference

```bash
# View all running services
screen -ls

# View specific service output
screen -r sensors     # Ctrl+A then D to detach
screen -r mavproxy
screen -r cam0
screen -r cam1

# Stop specific service
screen -X -S sensors quit
screen -X -S mavproxy quit
screen -X -S cam0 quit
screen -X -S cam1 quit

# Stop all services
./stop_all_services.sh

# Restart all services
./stop_all_services.sh && ./start_all_services.sh
```

---

## 🎉 You're All Set!

Once all services are running on the Raspberry Pi:

1. ✅ Launch `launch_mariner.py` on Windows
2. ✅ See live camera feeds
3. ✅ See real sensor data (depth, temperature, pressure)
4. ✅ Control thrusters with Nintendo Switch Pro Controller
5. ✅ ARM/DISARM via buttons or controller

**Happy Diving! 🌊🤖**
