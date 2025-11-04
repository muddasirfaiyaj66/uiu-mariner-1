# 🚨 FIX CONNECTION ERRORS - Quick Guide

## ❌ Problem

Your Windows application shows:

```
[WinError 10061] No connection could be made because the target machine actively refused it
```

## ✅ Solution

**The Raspberry Pi services are NOT running!** You need to start them.

---

## 🔧 STEPS TO FIX (On Raspberry Pi)

### Step 1: Copy Scripts to Pi

**From Windows PowerShell:**

```powershell
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

Password: `1234`

---

### Step 2: SSH to Raspberry Pi

```powershell
ssh pi@raspberrypi.local
```

Password: `1234`

---

### Step 3: Run Setup Script

```bash
cd ~/mariner/pi_scripts
chmod +x SETUP_AND_START.sh
./SETUP_AND_START.sh
```

**This script will:**

1. ✅ Make all scripts executable
2. ✅ Ask for your Windows PC IP address
3. ✅ Check Pixhawk connection (/dev/ttyACM0 at 115200)
4. ✅ Give you two options:
   - **A) Auto-start** (Services start on boot - RECOMMENDED)
   - **B) Manual start** (Start manually when needed)

**Choose Option A for automatic startup!**

---

### Step 4: Verify Services Running

```bash
# Check all services
screen -ls

# Or if you chose auto-start:
sudo systemctl status rov-sensors
sudo systemctl status rov-mavproxy
sudo systemctl status rov-camera0
sudo systemctl status rov-camera1
```

**Expected Output:**

```
✅ sensors
✅ mavproxy
✅ cam0
✅ cam1
```

---

### Step 5: Test on Windows

**Back to Windows PowerShell:**

```powershell
python launch_mariner.py
```

**Expected Result:**

```
✅ Pixhawk connected via tcp:raspberrypi.local:7000
✅ Sensors connected
✅ Camera 0 streaming
✅ Camera 1 streaming
✅ Controller connected
```

---

## 🎯 Quick Commands Reference

### On Raspberry Pi:

**View service logs:**

```bash
# Screen method (manual start)
screen -r sensors
screen -r mavproxy

# Systemd method (auto-start)
sudo journalctl -u rov-sensors -f
sudo journalctl -u rov-mavproxy -f
```

**Stop services:**

```bash
# Screen method
./stop_all_services.sh

# Systemd method
sudo systemctl stop rov-sensors rov-mavproxy rov-camera0 rov-camera1
```

**Restart services:**

```bash
# Screen method
./stop_all_services.sh
./start_all_services.sh YOUR_WINDOWS_IP

# Systemd method
sudo systemctl restart rov-sensors rov-mavproxy rov-camera0 rov-camera1
```

---

## 🔍 Troubleshooting

### If Pixhawk not found:

```bash
python3 detect_pixhawk.py
```

### If cameras not found:

```bash
./detect_cameras.sh
```

### If services won't start:

```bash
# Check Python is installed
python3 --version

# Check required packages
pip3 list | grep -E "pymavlink|adafruit-circuitpython-bmp3xx"

# Install if missing
pip3 install pymavlink adafruit-circuitpython-bmp3xx
```

### Check network connection:

```bash
# From Raspberry Pi, ping Windows PC
ping YOUR_WINDOWS_IP

# From Windows, ping Raspberry Pi
ping raspberrypi.local
```

---

## 📋 What Each Service Does

1. **rov-sensors** (Port 5000)

   - Reads BMP388 pressure sensor
   - Sends depth, temperature, pressure data

2. **rov-mavproxy** (Port 7000)

   - Connects to Pixhawk at /dev/ttyACM0 (115200 baud)
   - Provides TCP MAVLink interface

3. **rov-camera0** (UDP Port 5000)

   - Streams first camera to Windows PC
   - H.264 video over RTP/UDP

4. **rov-camera1** (UDP Port 5001)
   - Streams second camera to Windows PC
   - H.264 video over RTP/UDP

---

## ✅ Summary

**The issue:** Services not running on Raspberry Pi  
**The fix:** Run `./SETUP_AND_START.sh` on the Pi  
**Result:** Everything connects automatically!

🎉 **After setup, just power on the Pi and launch the Windows app!**
