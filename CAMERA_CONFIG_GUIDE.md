# Camera Configuration Guide

This guide explains how to detect and configure cameras for the UIU MARINER ROV system.

## Features

### 1. **Automatic Camera Detection**

The system can automatically detect cameras connected to the Raspberry Pi:

- **Pi Camera Modules** (via libcamera)
- **USB Webcams** (via v4l2)

### 2. **GUI Camera Selection**

The main GUI includes a camera configuration dialog with:

- Automatic camera scanning
- Camera source selection (dropdown)
- Port configuration for each camera
- Real-time pipeline preview
- Manual pipeline entry (advanced)

### 3. **Multiple Camera Support**

- Configure up to 2 cameras simultaneously
- Primary and secondary camera feeds
- Independent port assignments

---

## Quick Start

### On Raspberry Pi

#### 1. Run Camera Detection Script

```bash
# Make script executable
chmod +x /home/pi/mariner/detect_cameras.sh
chmod +x /home/pi/mariner/detect_cameras.py

# Detect cameras
./detect_cameras.sh

# Or use Python version for structured output
python3 detect_cameras.py
```

#### 2. Install Required Tools (if needed)

```bash
# For Pi Camera detection
sudo apt-get update
sudo apt-get install -y libcamera-apps libcamera-tools

# For USB camera detection
sudo apt-get install -y v4l2-utils

# For GStreamer (video streaming)
sudo apt-get install -y gstreamer1.0-tools gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good gstreamer1.0-plugins-bad
```

#### 3. Enable Pi Camera (if using Pi Camera Module)

```bash
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable
# Reboot after enabling
sudo reboot
```

---

### On Ground Station (Windows)

#### 1. Open Camera Configuration

In the MARINER GUI:

1. Click **"📹 Camera Settings"** button (in Control Panel)
2. Click **"🔍 Detect Available Cameras"**
3. Wait for camera detection to complete

#### 2. Select Cameras

- **Camera 0 (Primary)**: Select from dropdown
- **Camera 1 (Secondary)**: Select from dropdown
- Configure UDP ports (default: 5000, 5001)
- Preview the generated GStreamer pipeline

#### 3. Apply Configuration

1. Click **"Apply Configuration"**
2. Click **"🔄 Restart Cameras"** to apply changes

---

## Camera Detection Scripts

### Python Script (`detect_cameras.py`)

**Features:**

- Detects Pi Camera modules using `libcamera-hello --list-cameras`
- Detects USB cameras using `v4l2-ctl`
- Returns structured JSON output
- Filters out metadata devices
- Provides detailed camera information

**Usage:**

```bash
python3 detect_cameras.py
```

**Output Format:**

```json
{
  "success": true,
  "total": 2,
  "cameras": [
    {
      "id": 0,
      "type": "pi_camera",
      "name": "Pi Camera 0 (imx219)",
      "model": "imx219",
      "device": "/dev/video0",
      "interface": "libcamera"
    },
    {
      "id": 1,
      "type": "usb",
      "name": "USB Camera",
      "model": "HD Webcam",
      "device": "/dev/video1",
      "driver": "uvcvideo",
      "interface": "v4l2"
    }
  ],
  "pi_cameras": 1,
  "usb_cameras": 1
}
```

### Bash Script (`detect_cameras.sh`)

**Features:**

- Visual terminal output
- Step-by-step detection
- Troubleshooting guidance
- Installation instructions

**Usage:**

```bash
./detect_cameras.sh
```

---

## Camera Streaming

### From Raspberry Pi

#### Pi Camera

```bash
# Camera 0
python3 pi_camera_server.py 0 GROUND_STATION_IP 5000 --payload 96

# Camera 1
python3 pi_camera_server.py 1 GROUND_STATION_IP 5001 --payload 97
```

#### USB Camera

```bash
# Using GStreamer directly
gst-launch-1.0 v4l2src device=/dev/video0 ! \
    video/x-raw,width=640,height=480,framerate=30/1 ! \
    videoconvert ! x264enc tune=zerolatency ! \
    h264parse ! rtph264pay config-interval=1 pt=96 ! \
    udpsink host=GROUND_STATION_IP port=5000
```

---

## Troubleshooting

### Pi Camera Not Detected

**Symptoms:**

- `libcamera-hello --list-cameras` shows no cameras
- "No cameras available" error

**Solutions:**

1. **Check physical connection:**

   - Camera ribbon cable properly inserted
   - Blue side facing ethernet port (on Pi)
   - Contacts facing away from ethernet port

2. **Enable camera interface:**

   ```bash
   sudo raspi-config
   # Interface Options → Camera → Enable
   sudo reboot
   ```

3. **Check camera is recognized:**

   ```bash
   vcgencmd get_camera
   # Should show: supported=1 detected=1
   ```

4. **Update firmware:**
   ```bash
   sudo apt-get update
   sudo apt-get full-upgrade
   sudo reboot
   ```

### USB Camera Not Detected

**Symptoms:**

- No `/dev/video*` devices
- Camera not listed by `v4l2-ctl`

**Solutions:**

1. **Check USB connection:**

   ```bash
   lsusb
   # Should show camera device
   ```

2. **Check video devices:**

   ```bash
   ls -l /dev/video*
   ```

3. **Install v4l2-utils:**

   ```bash
   sudo apt-get install v4l2-utils
   ```

4. **Test camera:**
   ```bash
   v4l2-ctl --device=/dev/video0 --list-formats-ext
   ```

### GUI Cannot Detect Cameras

**Symptoms:**

- "Connection timeout" error
- "Cannot reach Raspberry Pi" message

**Solutions:**

1. **Check network connection:**

   ```bash
   # From Windows
   ping raspberrypi.local
   ```

2. **Check SSH is enabled on Pi:**

   ```bash
   sudo raspi-config
   # Interface Options → SSH → Enable
   ```

3. **Verify detection script exists:**

   ```bash
   ls -l /home/pi/mariner/detect_cameras.py
   ```

4. **Test SSH connection:**

   ```bash
   ssh pi@raspberrypi.local
   ```

5. **Manually run detection:**
   ```bash
   ssh pi@raspberrypi.local python3 /home/pi/mariner/detect_cameras.py
   ```

---

## GStreamer Pipelines

### Receiving on Ground Station (config.json)

#### Pi Camera (H.264)

```json
{
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  }
}
```

#### USB Camera (H.264)

```json
{
  "camera": {
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  }
}
```

---

## Advanced Configuration

### Custom Pipeline Entry

For advanced users, you can manually enter custom GStreamer pipelines in the camera configuration dialog.

**Example pipelines:**

1. **MJPEG Stream:**

   ```
   udpsrc port=5000 ! application/x-rtp,encoding-name=JPEG,payload=26 ! rtpjpegdepay ! jpegdec ! videoconvert ! appsink
   ```

2. **Raw Video (high bandwidth):**

   ```
   udpsrc port=5000 ! application/x-rtp,media=video,encoding-name=RAW ! rtpvrawdepay ! videoconvert ! appsink
   ```

3. **VP8 Stream:**
   ```
   udpsrc port=5000 ! application/x-rtp,encoding-name=VP8,payload=96 ! rtpvp8depay ! vp8dec ! videoconvert ! appsink
   ```

---

## Testing Camera Feeds

### Test on Raspberry Pi

```bash
# Test Pi Camera
libcamera-hello --timeout 5000

# Test USB Camera
gst-launch-1.0 v4l2src device=/dev/video0 ! videoconvert ! autovideosink
```

### Test Streaming

```bash
# On Pi - Start streaming
python3 pi_camera_server.py 0 192.168.0.100 5000

# On Ground Station - Test receiving
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
```

---

## File Structure

```
mariner-software-1.0/
├── pi_scripts/
│   ├── detect_cameras.sh          # Bash detection script
│   ├── detect_cameras.py          # Python detection script
│   ├── pi_camera_server.py        # Pi Camera streaming server
│   └── usb_camera_server.py       # USB Camera streaming server
├── src/
│   └── ui/
│       ├── cameraSelectionDialog.py   # Camera config GUI
│       ├── cameraWorker.py            # Camera feed processing
│       └── marinerApp.py              # Main application
└── config.json                    # Configuration file
```

---

## Support

For additional help:

1. Check TROUBLESHOOTING.md
2. Review QUICK_REFERENCE.md
3. Consult TESTING_GUIDE.md
4. Check Raspberry Pi camera documentation: https://www.raspberrypi.com/documentation/computers/camera_software.html
