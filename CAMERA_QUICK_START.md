# 🚀 Camera Setup - Quick Start

## Step 1: Setup Raspberry Pi (One Time Only)

### Copy Files to Pi

```powershell
# From Windows PowerShell
scp pi_scripts\detect_cameras.py pi@raspberrypi.local:/home/pi/mariner/
scp pi_scripts\detect_cameras.sh pi@raspberrypi.local:/home/pi/mariner/
scp pi_scripts\setup_camera_detection.sh pi@raspberrypi.local:/home/pi/mariner/
```

### Run Setup on Pi

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Make scripts executable
cd /home/pi/mariner
chmod +x *.sh
chmod +x *.py

# Run automated setup
./setup_camera_detection.sh
```

**The setup script will:**

- ✅ Install libcamera-apps
- ✅ Install v4l2-utils
- ✅ Copy detection scripts
- ✅ Test camera detection
- ✅ Check camera interface status

---

## Step 2: Enable Pi Camera (If Using Pi Camera)

```bash
# On Raspberry Pi
sudo raspi-config

# Navigate to:
# 3 Interface Options
#   → Camera
#     → Enable

# Reboot
sudo reboot
```

---

## Step 3: Test Camera Detection (On Pi)

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Run detection
python3 /home/pi/mariner/detect_cameras.py
```

**Expected Output:**

```json
{
  "success": true,
  "total": 2,
  "cameras": [
    {
      "id": 0,
      "type": "pi_camera",
      "name": "Pi Camera 0 (imx219)",
      "device": "/dev/video0"
    },
    {
      "id": 1,
      "type": "usb",
      "name": "HD Webcam",
      "device": "/dev/video1"
    }
  ]
}
```

---

## Step 4: Configure Cameras in GUI (On Windows)

### Open Camera Settings

1. **Launch MARINER** application
2. **Look at Control Panel** (right side)
3. **Click "📹 Camera Settings"**

### Detect Cameras

4. **Click "🔍 Detect Available Cameras"**
5. **Wait 5-10 seconds** for detection
6. **See message**: "✅ Found X cameras..."

### Select Cameras

7. **Camera 0 dropdown** → Select your primary camera
8. **Camera 1 dropdown** → Select your secondary camera
9. **Ports**: Keep default (5000, 5001) or change if needed

### Apply Configuration

10. **Click "Apply Configuration"**
11. **Click "🔄 Restart Cameras"**
12. **Video feeds appear!** 🎥

---

## Step 5: Start Streaming (On Pi)

### Option A: Use Existing Scripts

```bash
# For Camera 0 (Pi Camera)
python3 /home/pi/mariner/pi_camera_server.py 0 192.168.0.100 5000

# For Camera 1
python3 /home/pi/mariner/pi_camera_server.py 1 192.168.0.100 5001
```

### Option B: Use Service Scripts (Automated)

```bash
# Start all services
/home/pi/mariner/start_all_services.sh
```

---

## 🎯 Quick Commands

### Detection

```bash
# Detect cameras (Python)
python3 /home/pi/mariner/detect_cameras.py

# Detect cameras (Bash - verbose)
/home/pi/mariner/detect_cameras.sh
```

### Testing

```bash
# Test Pi Camera
libcamera-hello --timeout 5000

# List video devices
ls -l /dev/video*

# Check camera status
vcgencmd get_camera
```

### Troubleshooting

```bash
# Check if services running
ps aux | grep camera

# Kill stuck processes
pkill -f camera

# Restart services
sudo systemctl restart rov_services
```

---

## ⚠️ Common Issues

### Issue: "No cameras detected"

```bash
# Check physical connection
vcgencmd get_camera  # Should show: detected=1

# Enable camera interface
sudo raspi-config → Interface → Camera → Enable
sudo reboot
```

### Issue: "Connection timeout"

```bash
# Test network
ping raspberrypi.local

# Test SSH
ssh pi@raspberrypi.local

# Check SSH enabled
sudo raspi-config → Interface → SSH → Enable
```

### Issue: "No video feed"

```bash
# Check streaming on Pi
ps aux | grep camera

# Check ports
netstat -an | grep 5000

# Restart cameras from GUI
Click "🔄 Restart Cameras"
```

---

## 📚 Full Documentation

| Document                     | Description                        |
| ---------------------------- | ---------------------------------- |
| `IMPLEMENTATION_COMPLETE.md` | Complete feature overview          |
| `CAMERA_CONFIG_GUIDE.md`     | Detailed setup and troubleshooting |
| `CAMERA_QUICK_REF.md`        | Quick reference commands           |
| `CAMERA_VISUAL_GUIDE.md`     | Visual workflows and diagrams      |

---

## ✅ Checklist

Before first use:

- [ ] Scripts copied to Pi
- [ ] Setup script executed
- [ ] libcamera-apps installed
- [ ] v4l2-utils installed
- [ ] Camera interface enabled
- [ ] Pi rebooted
- [ ] Detection tested manually

For each session:

- [ ] Network connected
- [ ] Cameras connected
- [ ] Detection successful
- [ ] GUI configured
- [ ] Streaming started
- [ ] Video feeds visible

---

## 🎉 That's It!

**Your camera system is now ready to use!**

Just open the GUI, click "📹 Camera Settings", detect cameras, select them, and start streaming! 🚀

For help: See `CAMERA_CONFIG_GUIDE.md`
