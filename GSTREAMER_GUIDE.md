# GStreamer Installation Guide (Windows) 🎥

## Why GStreamer?

GStreamer is needed for:

- ✅ Receiving H.264 video streams from ROV cameras
- ✅ Decoding video in real-time
- ✅ Low-latency video display

**Without GStreamer:** Camera feeds won't work (you'll see "Failed to open stream")  
**With test patterns:** Works without GStreamer for testing GUI

---

## Quick Installation (Windows)

### Step 1: Download GStreamer

Visit: https://gstreamer.freedesktop.org/download/

Download **BOTH** installers:

1. **Runtime Installer** (required)
   - `gstreamer-1.0-msvc-x86_64-1.24.10.msi` (or latest version)
2. **Development Installer** (required for OpenCV)
   - `gstreamer-1.0-devel-msvc-x86_64-1.24.10.msi` (or latest version)

### Step 2: Install Runtime

1. Run `gstreamer-1.0-msvc-x86_64-1.24.10.msi`
2. Choose **Complete** installation (important!)
3. Default location: `C:\gstreamer\1.0\msvc_x86_64\`
4. Click through installer
5. ✅ Runtime installed

### Step 3: Install Development

1. Run `gstreamer-1.0-devel-msvc-x86_64-1.24.10.msi`
2. Choose **Complete** installation
3. Same location: `C:\gstreamer\1.0\msvc_x86_64\`
4. Click through installer
5. ✅ Development installed

### Step 4: Add to PATH

**Option A: Automatic (PowerShell as Administrator)**

```powershell
# Run PowerShell as Administrator
$gstPath = "C:\gstreamer\1.0\msvc_x86_64\bin"
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$gstPath", "Machine")

# Restart terminal for changes to take effect
```

**Option B: Manual**

1. Open **System Properties**
   - Win+R → `sysdm.cpl` → Enter
2. Click **Advanced** tab → **Environment Variables**
3. Under **System variables**, find **Path**
4. Click **Edit** → **New**
5. Add: `C:\gstreamer\1.0\msvc_x86_64\bin`
6. Click **OK** on all dialogs
7. **Restart terminal/computer**

### Step 5: Verify Installation

Open **new** terminal (PowerShell or CMD):

```powershell
# Check GStreamer version
gst-inspect-1.0 --version

# Should show:
# gst-inspect-1.0 version 1.24.10
# GStreamer 1.24.10
# ...
```

Test a pipeline:

```powershell
# Test video source
gst-launch-1.0 videotestsrc ! autovideosink
```

You should see a test pattern window. Press Ctrl+C to stop.

---

## Integration with OpenCV

### Check if OpenCV has GStreamer Support

```powershell
# Activate your virtual environment first
.\venv\Scripts\Activate.ps1

# Check OpenCV build info
python -c "import cv2; print(cv2.getBuildInformation())" | Select-String -Pattern "GStreamer"
```

**Expected output:**

```
GStreamer:                   YES (1.24.10)
```

**If shows NO:**
You need opencv-python compiled with GStreamer support.

### Fix: Install opencv-python with GStreamer

Unfortunately, the pip version of opencv-python may not have GStreamer support on Windows.

**Options:**

**Option 1: Use Test Patterns (Easiest)**
Edit `config.json`:

```json
{
  "camera": {
    "pipeline0": "videotestsrc pattern=smpte ! videoconvert ! appsink",
    "pipeline1": "videotestsrc pattern=ball ! videoconvert ! appsink"
  }
}
```

This works WITHOUT GStreamer for GUI testing.

**Option 2: Use Camera Index (USB Cameras)**

```json
{
  "camera": {
    "pipeline0": "0",
    "pipeline1": "1"
  }
}
```

Works with USB cameras without GStreamer.

**Option 3: Build OpenCV with GStreamer (Advanced)**
See: https://docs.opencv.org/master/d3/d52/tutorial_windows_install.html

**Option 4: Use opencv-python-headless**

```powershell
pip uninstall opencv-python
pip install opencv-python-headless
```

May have better GStreamer support.

---

## Testing Camera Pipelines

### Test GStreamer Pipeline Directly

```powershell
# Test UDP receiver (port 5000)
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink

# Test file playback
gst-launch-1.0 filesrc location=test.mp4 ! decodebin ! videoconvert ! autovideosink

# Test pattern (no network needed)
gst-launch-1.0 videotestsrc ! videoconvert ! autovideosink
```

If these work, GStreamer is installed correctly!

### Test in Python

```python
import cv2

# Test GStreamer pipeline
pipeline = "videotestsrc ! videoconvert ! appsink"
cap = cv2.VideoCapture(pipeline, cv2.CAP_GSTREAMER)

if cap.isOpened():
    print("✅ GStreamer working!")
    ret, frame = cap.read()
    if ret:
        print(f"✅ Frame received: {frame.shape}")
        cv2.imshow("Test", frame)
        cv2.waitKey(1000)
else:
    print("❌ GStreamer not working")

cap.release()
cv2.destroyAllWindows()
```

Save as `test_gstreamer.py` and run:

```powershell
python test_gstreamer.py
```

---

## Configuration for Real ROV Cameras

Once GStreamer is working, use this config for real camera streams:

```json
{
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  }
}
```

This receives H.264 video from Raspberry Pi cameras on ports 5000 and 5001.

---

## Raspberry Pi Camera Streaming Setup

On your ROV's Raspberry Pi, stream cameras with:

```bash
# Camera 0 to port 5000
raspivid -t 0 -w 1280 -h 720 -fps 30 -b 2000000 -o - | \
  gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=96 ! \
  udpsink host=192.168.0.100 port=5000

# Camera 1 to port 5001
raspivid -cs 1 -t 0 -w 1280 -h 720 -fps 30 -b 2000000 -o - | \
  gst-launch-1.0 -v fdsrc ! h264parse ! rtph264pay config-interval=10 pt=97 ! \
  udpsink host=192.168.0.100 port=5001
```

Replace `192.168.0.100` with your Ground Station PC IP.

---

## Troubleshooting

### "gst-inspect-1.0 not recognized"

**Cause:** GStreamer not in PATH  
**Fix:** Add to PATH (see Step 4 above) and restart terminal

### "Failed to open stream" in application

**Cause:** Several possibilities

**Check 1: GStreamer installed?**

```powershell
gst-inspect-1.0 --version
```

**Check 2: OpenCV has GStreamer?**

```powershell
python -c "import cv2; print(cv2.getBuildInformation())" | Select-String -Pattern "GStreamer"
```

**Check 3: Try test pattern**
Edit config.json:

```json
"pipeline0": "videotestsrc ! videoconvert ! appsink"
```

**Check 4: Try camera index**

```json
"pipeline0": "0"
```

### "Could not load plugin" errors

**Cause:** Incomplete GStreamer installation  
**Fix:**

1. Uninstall GStreamer (Control Panel)
2. Reinstall with **Complete** option
3. Restart computer

### Video lags or stutters

**Cause:** Network or decoding issues  
**Fix:**

- Lower camera resolution on Pi
- Reduce bitrate: `-b 1000000`
- Check WiFi signal strength
- Use wired Ethernet if possible

### Black screen / No video

**Cause:** Pi not streaming or wrong IP

**Test Pi is streaming:**

```powershell
# On Ground Station PC
gst-launch-1.0 udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! autovideosink
```

If you see video, GStreamer works! Problem is in application.

---

## Alternative: Skip GStreamer for Testing

You can test the entire application **without** GStreamer:

### Use Test Patterns

`config.json`:

```json
{
  "camera": {
    "pipeline0": "videotestsrc pattern=smpte ! videoconvert ! appsink",
    "pipeline1": "videotestsrc pattern=ball ! videoconvert ! appsink"
  }
}
```

**Works on:** Any system with OpenCV  
**Shows:** Test patterns in camera windows  
**Good for:** Testing GUI, joystick, controls, sensors

### Use USB Cameras

`config.json`:

```json
{
  "camera": {
    "pipeline0": "0",
    "pipeline1": "1"
  }
}
```

**Works with:** Built-in webcam or USB cameras  
**Shows:** Real camera feed  
**Good for:** Testing object detection

---

## Summary

### Minimum (Testing Only):

```
✅ Python 3.8+
✅ Virtual environment
✅ pip install -r requirements.txt
✅ Test patterns in config.json
```

### Full Setup (Real Cameras):

```
✅ Everything above, plus:
✅ GStreamer runtime installed
✅ GStreamer development installed
✅ GStreamer in PATH
✅ OpenCV with GStreamer support
✅ Real camera pipelines in config.json
✅ Raspberry Pi streaming cameras
```

---

## Quick Test Script

Save as `test_camera_setup.py`:

```python
import sys
import cv2

print("Testing camera setup...\n")

# Test 1: OpenCV installed
try:
    print(f"✅ OpenCV version: {cv2.__version__}")
except:
    print("❌ OpenCV not installed")
    sys.exit(1)

# Test 2: GStreamer support
build_info = cv2.getBuildInformation()
if "GStreamer" in build_info and "YES" in build_info:
    print("✅ OpenCV has GStreamer support")
else:
    print("⚠️ OpenCV missing GStreamer support")
    print("   You can still use test patterns or USB cameras")

# Test 3: Test pattern
print("\nTesting video capture...")
cap = cv2.VideoCapture(0)  # Try index 0
if cap.isOpened():
    print("✅ Camera index 0 works (USB camera?)")
    cap.release()
else:
    print("⚠️ No camera on index 0 (OK if using network cameras)")

print("\n✅ Basic setup OK!")
print("Run application: python launch_mariner.py")
```

Run:

```powershell
python test_camera_setup.py
```

---

_GStreamer Installation Guide v1.0_  
_UIU MARINER ROV Control System_
