# ✅ UPDATES APPLIED - Thruster Logging & Camera/Pixhawk Detection

## 🎮 Issue 1: FIXED - Joystick Thruster Logging

**Problem:** Joystick movements weren't showing which thruster pins were being controlled

**Solution:** Added detailed logging to `joystickController.py`

### New Output When Moving Joystick:

```
[THRUSTER] Forward/Back: -0.85 → Ch1(Pin1)=1300, Ch8(Pin8)=1700
[THRUSTER] Left/Right: 0.42 → Ch2(Pin2)=1600, Ch5(Pin5)=1400
[THRUSTER] Up/Down: 0.65 → Ch3(Pin3)=1650, Ch4(Pin4)=1650, Ch6(Pin6)=1350, Ch7(Pin7)=1350
[THRUSTER] ⚠️ EMERGENCY STOP - All channels set to neutral (1500μs)
```

### Thruster Channel Mapping:

- **Ch1 (Pin 1)** - Forward/Backward (ACW)
- **Ch2 (Pin 2)** - Left/Right rotation
- **Ch3 (Pin 3)** - Up/Down (ACW)
- **Ch4 (Pin 4)** - Up/Down (ACW)
- **Ch5 (Pin 5)** - Left/Right rotation (opposite)
- **Ch6 (Pin 6)** - Up/Down (CW)
- **Ch7 (Pin 7)** - Up/Down (CW)
- **Ch8 (Pin 8)** - Forward/Backward (CW)

**Note:** Thruster commands only sent when Pixhawk is CONNECTED and ARMED!

---

## 📹 Issue 2: FIXED - Pi Camera & USB Webcam Support

**Problem:** Need to detect and configure Pi Camera Module and USB webcams

**Solution:** Created detection and streaming scripts

### New Scripts Created:

#### 1. `detect_cameras.sh` - Camera Detection

Automatically detects:

- Raspberry Pi Camera Module (via libcamera)
- USB webcams (/dev/video\*)
- Shows device capabilities

**Usage:**

```bash
cd ~/mariner/pi_scripts
./detect_cameras.sh
```

#### 2. `usb_camera_server.py` - USB Webcam Streaming

Stream from USB webcam via GStreamer UDP/RTP

**Usage:**

```bash
python3 usb_camera_server.py /dev/video0 192.168.0.104 5000 --payload 96
```

#### 3. `usb_cam0.sh` & `usb_cam1.sh` - Quick Start Scripts

Convenient shortcuts for USB camera streaming

**Usage:**

```bash
./usb_cam0.sh 192.168.0.104   # Stream USB camera 0
./usb_cam1.sh 192.168.0.104   # Stream USB camera 1
```

### Camera Configuration Options:

**Option A: Pi Camera Module (CSI)**

```bash
./cam0.sh 192.168.0.104        # Use existing script
```

**Option B: USB Webcam**

```bash
./usb_cam0.sh 192.168.0.104    # Use new USB script
```

**Option C: Mixed (Pi + USB)**

```bash
./cam0.sh 192.168.0.104        # Pi camera on port 5000
./usb_cam1.sh 192.168.0.104    # USB camera on port 5001
```

---

## 🔌 Issue 3: FIXED - Pixhawk Connection Detection

**Problem:** Need to automatically find Pixhawk serial port and baud rate

**Solution:** Created comprehensive detection script

### New Script: `detect_pixhawk.py`

Automatically scans:

- **Ports:** `/dev/ttyAMA0`, `/dev/serial0`, `/dev/ttyUSB0`, `/dev/ttyACM0`, etc.
- **Baud Rates:** 115200, 57600, 38400, 19200, 9600
- **Tests:** Waits for MAVLink HEARTBEAT message

**Usage:**

```bash
cd ~/mariner/pi_scripts
python3 detect_pixhawk.py
```

### Expected Output:

```
✅ PIXHAWK FOUND!
Port: /dev/ttyACM0
Baud Rate: 57600

🔧 Use these settings in your configuration:
   MAVLink Master: /dev/ttyACM0
   Baud Rate: 57600

📝 Update pi_mavproxy_server.py with:
   --master /dev/ttyACM0 --baudrate 57600
```

### Common Pixhawk Connections:

| Connection Type | Port         | Default Baud    |
| --------------- | ------------ | --------------- |
| **USB**         | /dev/ttyACM0 | 57600 or 115200 |
| **UART (GPIO)** | /dev/serial0 | 57600           |
| **USB-Serial**  | /dev/ttyUSB0 | 57600           |

---

## 📋 Complete Setup Workflow

### 1️⃣ Copy Scripts to Pi

```powershell
# From Windows
cd "E:\UIU MARINER\mariner-software-1.0"
scp -r pi_scripts pi@raspberrypi.local:~/mariner/
```

### 2️⃣ SSH to Pi

```bash
ssh pi@raspberrypi.local
cd ~/mariner/pi_scripts
chmod +x *.sh *.py
```

### 3️⃣ Detect Hardware

```bash
# Find Pixhawk
python3 detect_pixhawk.py

# Find Cameras
./detect_cameras.sh
```

### 4️⃣ Update Configuration

**If Pixhawk is on different port/baud:**

```bash
nano pi_mavproxy_server.py
# Change --master and --baudrate
```

**If using USB cameras:**

```bash
nano start_all_services.sh
# Change cam0.sh to usb_cam0.sh
# Change cam1.sh to usb_cam1.sh
```

### 5️⃣ Start Services

```bash
./start_all_services.sh 192.168.0.104
```

### 6️⃣ Launch Application (Windows)

```powershell
cd "E:\UIU MARINER\mariner-software-1.0"
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

## 🎯 What You Should Now See

### On Windows Application:

**Connection Status:**

```
[PIXHAWK] ✅ Connected via tcp:raspberrypi.local:7000
[SENSORS] ✅ Connected - Depth: 0.5m, Temp: 24.3°C
[CAM0] ✅ Stream started - 640x480@30fps
[CAM1] ✅ Stream started - 640x480@30fps
[JOYSTICK] ✅ Connected: Nintendo Switch Pro Controller
```

**Joystick Control:**

```
[THRUSTER] Forward/Back: -0.85 → Ch1(Pin1)=1300, Ch8(Pin8)=1700
[THRUSTER] Left/Right: 0.42 → Ch2(Pin2)=1600, Ch5(Pin5)=1400
[THRUSTER] Up/Down: 0.65 → Ch3(Pin3)=1650, Ch4(Pin4)=1650, Ch6(Pin6)=1350, Ch7(Pin7)=1350
```

### On Raspberry Pi:

```bash
screen -ls
# Shows: sensors, mavproxy, cam0, cam1 all running

screen -r mavproxy
# Shows: HEARTBEAT messages from Pixhawk

screen -r cam0
# Shows: GStreamer pipeline streaming video
```

---

## 🔧 Troubleshooting

### Still Getting `[WinError 10061]`?

**Run detection scripts on Pi:**

```bash
python3 detect_pixhawk.py     # Find correct port/baud
./detect_cameras.sh            # Find camera devices
```

**Update pi_mavproxy_server.py with detected values**

### No Thruster Logs?

**Requirements:**

1. ✅ Pixhawk must be connected (no `[WinError 10061]`)
2. ✅ System must be ARMED
3. ✅ Move joysticks with decent deflection (>10%)

**If still not working:**

```bash
# On Pi, check MAVProxy is receiving commands
screen -r mavproxy
# Should show RC_CHANNELS_OVERRIDE messages
```

### Camera Not Working?

**Run detection:**

```bash
./detect_cameras.sh
```

**Test directly:**

```bash
# Pi Camera
libcamera-hello --camera 0 -t 5000

# USB Camera
v4l2-ctl --device=/dev/video0 --all
```

---

## 📚 Documentation

- **`COMPLETE_SETUP_GUIDE.md`** - Full step-by-step guide
- **`detect_pixhawk.py`** - Pixhawk port/baud detection
- **`detect_cameras.sh`** - Camera detection
- **`usb_camera_server.py`** - USB webcam streaming
- **`usb_cam0.sh` / `usb_cam1.sh`** - USB camera shortcuts

---

## ✅ Summary

1. ✅ **Thruster logging** - Now shows channel numbers and PWM values
2. ✅ **Camera detection** - Detects both Pi Camera and USB webcams
3. ✅ **USB camera support** - New streaming scripts for USB cameras
4. ✅ **Pixhawk detection** - Automatically finds correct port/baud
5. ✅ **Complete guide** - Step-by-step setup documentation

**Next: Run the detection scripts on your Raspberry Pi!** 🍓🔍
