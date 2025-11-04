# 🚨 URGENT FIX - Missing Dependencies on Pi

## ⚠️ Current Status

**Good News:** MAVProxy is running! ✅

**Bad News:** Cameras and sensors failed because packages aren't installed ❌

---

## 🔧 Fix It Now (3 Commands)

### On Raspberry Pi (via SSH):

```bash
# 1. Copy install script to Pi
exit  # (if you're still in SSH)
```

Then from Windows:

```powershell
scp pi_scripts\INSTALL_DEPENDENCIES.sh pi@raspberrypi.local:~/mariner/pi_scripts/
```

Then SSH back in:

```powershell
ssh pi@raspberrypi.local
```

```bash
# 2. Make it executable and run it
chmod +x ~/mariner/pi_scripts/INSTALL_DEPENDENCIES.sh
~/mariner/pi_scripts/INSTALL_DEPENDENCIES.sh

# 3. Start services again
cd ~/mariner/pi_scripts
./START_NOW.sh 192.168.0.104
```

---

## 🎯 What's Being Installed

| Package                         | Purpose               | Status     |
| ------------------------------- | --------------------- | ---------- |
| `libcamera-apps`                | Pi Camera support     | ❌ Missing |
| `gstreamer1.0-*`                | Video streaming       | ❌ Missing |
| `mavproxy`                      | Pixhawk communication | ✅ Running |
| `python3-pip`                   | Python packages       | ?          |
| `adafruit-circuitpython-bmp3xx` | Sensor support        | ❌ Missing |

---

## ⚡ Quick One-Liner (from Pi)

```bash
cd ~/mariner/pi_scripts && chmod +x INSTALL_DEPENDENCIES.sh && ./INSTALL_DEPENDENCIES.sh && ./START_NOW.sh 192.168.0.104
```

---

## 🔍 Why Services Failed

**Cameras:**

```
/bin/bash: line 2: libcamera-vid: command not found
/bin/bash: line 2: gst-launch-1.0: command not found
```

**Fix:** Install libcamera-apps and gstreamer

**Sensors:**

```
❌ Fatal error: [Errno 2] No such file or directory
```

**Fix:** Install adafruit-circuitpython-bmp3xx

**MAVProxy:**

```
✅ MAVProxy: RUNNING (PID: 15135)
```

**Status:** Already working!

---

## 📝 Manual Installation (if script fails)

```bash
# Update
sudo apt-get update

# Install camera support
sudo apt-get install -y libcamera-apps libcamera-tools

# Install GStreamer
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad \
    gstreamer1.0-plugins-ugly gstreamer1.0-libav

# Install Python packages
sudo apt-get install -y python3-pip
sudo pip3 install pymavlink mavproxy adafruit-circuitpython-bmp3xx

# Install v4l2-utils
sudo apt-get install -y v4l2-utils
```

---

## ✅ After Installation

Run this to verify:

```bash
# Check libcamera
libcamera-hello --version

# Check GStreamer
gst-launch-1.0 --version

# Check MAVProxy
mavproxy.py --help

# Check Python packages
python3 -c "import adafruit_bmp3xx; print('BMP3XX OK')"
```

Then start services:

```bash
cd ~/mariner/pi_scripts
./START_NOW.sh 192.168.0.104
```

---

## 🎉 Expected Output After Fix

```
==========================================
📊 SERVICE STATUS
==========================================
✅ Sensor Server:  RUNNING (PID: XXXX)
✅ MAVProxy:       RUNNING (PID: XXXX)
✅ Camera 0:       RUNNING (PID: XXXX)
✅ Camera 1:       RUNNING (PID: XXXX)
```

Then on Windows:

```powershell
python launch_mariner.py
```

Should see:

```
[✅] Heartbeat received — Pixhawk Connected!
[CAMERAS] ✅ Dual camera feeds started
[SENSORS] ✅ Connected to sensor server
```

---

## 🚀 DO THIS NOW

Copy and paste this into your SSH session:

```bash
cd ~/mariner/pi_scripts && chmod +x *.sh && ./INSTALL_DEPENDENCIES.sh
```

This will install everything needed. Takes about 5-10 minutes.
