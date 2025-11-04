# Camera Configuration - Quick Reference

## 🎯 Quick Actions

### Detect Cameras on Pi

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Run detection
python3 /home/pi/mariner/detect_cameras.py
```

### Configure Cameras in GUI

1. Open MARINER GUI
2. Click **"📹 Camera Settings"**
3. Click **"🔍 Detect Available Cameras"**
4. Select cameras from dropdowns
5. Click **"Apply Configuration"**
6. Click **"🔄 Restart Cameras"**

---

## 📹 Camera Detection

### What Gets Detected?

- ✅ **Pi Camera Modules** (CSI interface)
- ✅ **USB Webcams** (USB interface)
- ✅ **Multiple cameras** (up to 2 simultaneously)

### Detection Methods

| Method        | Command                     | Output         |
| ------------- | --------------------------- | -------------- |
| Bash Script   | `./detect_cameras.sh`       | Human-readable |
| Python Script | `python3 detect_cameras.py` | JSON format    |
| GUI           | Camera Settings → Detect    | Interactive    |

---

## 🔧 Common Issues

### Issue: Pi Camera Not Found

**Check:**

```bash
# 1. Is camera enabled?
sudo raspi-config
# → Interface Options → Camera → Enable

# 2. Is camera recognized?
vcgencmd get_camera
# Should show: supported=1 detected=1

# 3. Are libcamera tools installed?
which libcamera-hello
# Should show path, otherwise install:
sudo apt-get install -y libcamera-apps
```

**Test:**

```bash
libcamera-hello --list-cameras
# Should list available cameras
```

---

### Issue: USB Camera Not Found

**Check:**

```bash
# 1. Is camera plugged in?
lsusb
# Should show USB camera device

# 2. Are video devices present?
ls -l /dev/video*
# Should list /dev/video0, /dev/video1, etc.

# 3. Are v4l2 tools installed?
which v4l2-ctl
# Should show path, otherwise install:
sudo apt-get install -y v4l2-utils
```

**Test:**

```bash
v4l2-ctl --device=/dev/video0 --list-formats-ext
# Should show supported formats
```

---

### Issue: GUI Can't Detect Cameras

**Check:**

1. **Network connectivity:**

   ```powershell
   ping raspberrypi.local
   ```

2. **SSH access:**

   ```powershell
   ssh pi@raspberrypi.local
   ```

3. **Detection script exists:**

   ```bash
   ls -l /home/pi/mariner/detect_cameras.py
   ```

4. **Run manually:**
   ```bash
   ssh pi@raspberrypi.local python3 /home/pi/mariner/detect_cameras.py
   ```

---

## 📝 Configuration Files

### config.json Structure

```json
{
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  }
}
```

### Default Ports

| Camera   | Port | Payload |
| -------- | ---- | ------- |
| Camera 0 | 5000 | 96      |
| Camera 1 | 5001 | 97      |

---

## 🚀 Start Streaming

### On Raspberry Pi

**Pi Camera:**

```bash
python3 pi_camera_server.py 0 192.168.0.100 5000 --payload 96
```

**USB Camera:**

```bash
gst-launch-1.0 v4l2src device=/dev/video0 ! \
    video/x-raw,width=640,height=480,framerate=30/1 ! \
    videoconvert ! x264enc tune=zerolatency ! \
    h264parse ! rtph264pay config-interval=1 pt=96 ! \
    udpsink host=192.168.0.100 port=5000
```

### On Ground Station

**Configure in GUI:**

1. Camera Settings → Detect Cameras
2. Select camera sources
3. Apply Configuration
4. Restart Cameras

**Or edit config.json manually and restart app**

---

## 🎛️ GUI Controls

### Camera Panel Buttons

| Button                  | Function                             |
| ----------------------- | ------------------------------------ |
| 📹 **Camera Settings**  | Open camera configuration dialog     |
| 🔄 **Restart Cameras**  | Restart camera feeds with new config |
| 👁️ **Toggle Detection** | Enable/disable object detection      |

### Camera Status Indicators

| Display                      | Meaning                    |
| ---------------------------- | -------------------------- |
| 🎥 Waiting for video feed... | No video received          |
| CAM 1 badge                  | Camera ID overlay on video |
| DETECT: ON/OFF               | Object detection status    |

---

## 💡 Pro Tips

1. **Always detect cameras first** before configuring
2. **Use consistent ports** (5000 for cam0, 5001 for cam1)
3. **Test cameras individually** before running both
4. **Check network bandwidth** for multiple HD streams
5. **Enable GStreamer debug** if streams fail:
   ```bash
   export GST_DEBUG=3
   python3 pi_camera_server.py 0 192.168.0.100 5000
   ```

---

## 📚 Related Documentation

- **Full Guide:** CAMERA_CONFIG_GUIDE.md
- **Troubleshooting:** TROUBLESHOOTING.md
- **Testing:** TESTING_GUIDE.md
- **Quick Start:** QUICKSTART.md

---

## ⚡ One-Line Commands

```bash
# Detect all cameras
ssh pi@raspberrypi.local python3 /home/pi/mariner/detect_cameras.py

# Test Pi Camera
ssh pi@raspberrypi.local libcamera-hello --timeout 5000

# List USB cameras
ssh pi@raspberrypi.local "ls -l /dev/video*"

# Check camera status
ssh pi@raspberrypi.local vcgencmd get_camera

# Install camera tools
ssh pi@raspberrypi.local "sudo apt-get install -y libcamera-apps v4l2-utils"
```

---

**Need Help?** See CAMERA_CONFIG_GUIDE.md for detailed troubleshooting.
