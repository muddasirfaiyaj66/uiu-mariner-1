# Direct Pixhawk Serial Connection - Quick Guide

## ✅ What Changed

Your `config.json` has been updated to use **direct serial connection** to Pixhawk:

```json
{
  "mavlink_connection": "/dev/ttyACM0:115200"
}
```

This means:

- ✅ **No need for MAVProxy** server on Pi
- ✅ **Direct USB connection** from Pi to Pixhawk
- ✅ **Faster response** - no network layer
- ✅ **More reliable** - no TCP timeout issues

---

## 🔌 Hardware Setup

### Connection:

```
Pixhawk USB Port → Raspberry Pi USB Port
```

### Port Detection:

The Pixhawk typically appears as:

- **Most common:** `/dev/ttyACM0` at 115200 baud ✅ (now default)
- **Alternative:** `/dev/ttyUSB0` (if using FTDI adapter)
- **GPIO UART:** `/dev/ttyAMA0` or `/dev/serial0`

---

## 🧪 Testing Connection

### On Raspberry Pi:

#### 1. Check if Pixhawk is Connected

```bash
ls -l /dev/ttyACM*
# Should show: /dev/ttyACM0
```

#### 2. Check Device Permissions

```bash
# Add pi user to dialout group (if not already)
sudo usermod -a -G dialout pi

# May need to logout/login or reboot
sudo reboot
```

#### 3. Test with MAVProxy (Optional)

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
# Should show: "Heartbeat received"
```

#### 4. List USB Devices

```bash
lsusb
# Should show something like: "3D Robotics PX4 FMU v2.x"
```

---

## 🎛️ Camera Settings Now Visible!

The camera configuration buttons are now **prominently displayed** in the Control Panel:

```
┌────────────────────────────┐
│   CONTROL PANEL            │
├────────────────────────────┤
│  [🔓 ARM THRUSTERS]        │
│  [⚠️ EMERGENCY STOP]       │
│  [👁️ Toggle Detection]     │
│                            │
│  ──────────────────────    │
│  📹 CAMERA CONTROLS        │
│                            │
│  [📹 Camera Settings]      │  ← Orange button, 50px high
│  [🔄 Restart Cameras]      │  ← Yellow button, 45px high
└────────────────────────────┘
```

### Button Styling:

- **📹 Camera Settings** - Orange (#FF8800), large, bold
- **🔄 Restart Cameras** - Yellow (#FFB800), prominent
- Clear separation with label and line

---

## 🚀 Quick Start

### 1. Connect Hardware

```bash
# Plug Pixhawk USB into Raspberry Pi USB port
# Wait 5 seconds for device to enumerate
```

### 2. Verify Connection (on Pi)

```bash
ssh pi@raspberrypi.local
ls -l /dev/ttyACM0
# Should exist
```

### 3. Launch MARINER (on Windows)

```powershell
python launch_mariner.py
```

### Expected Output:

```
[CONNECT] Attempting to connect → /dev/ttyACM0:115200
[✅] Heartbeat received — Pixhawk Connected!
    System ID: 1, Component ID: 1
```

---

## 🔧 If Connection Fails

### Issue: "No such file or directory: /dev/ttyACM0"

**Solution 1: Check USB Connection**

```bash
# List USB devices
lsusb

# Check for ttyACM or ttyUSB
ls -l /dev/tty*
```

**Solution 2: Try Different Port**
Edit `config.json`:

```json
{
  "mavlink_connection": "/dev/ttyUSB0:115200"
}
```

**Solution 3: Enable Auto-Detect**
Edit `config.json`:

```json
{
  "mavlink_auto_detect": true
}
```

This will scan all ports automatically if the default fails.

---

### Issue: "Permission denied"

**Solution:**

```bash
# Add user to dialout group
sudo usermod -a -G dialout pi

# Logout and login again, or reboot
sudo reboot
```

---

### Issue: Still showing "tcp:raspberrypi.local:7000"

**Solution:**
The config has been updated. If you want to switch back to TCP/MAVProxy:

```json
{
  "mavlink_connection": "tcp:raspberrypi.local:7000"
}
```

---

## 📊 Comparison

| Connection Type   | Latency   | Setup   | Reliability |
| ----------------- | --------- | ------- | ----------- |
| **Direct Serial** | ⚡ Low    | Simple  | ⭐⭐⭐⭐⭐  |
| **TCP/MAVProxy**  | 🐌 Higher | Complex | ⭐⭐⭐      |

**Recommendation:** Use direct serial (current config) ✅

---

## 🎥 Camera Configuration

Now that the buttons are visible:

### 1. Open Camera Settings

Click the orange **"📹 Camera Settings"** button

### 2. Detect Cameras

Click **"🔍 Detect Available Cameras"**

### 3. Select & Apply

- Choose cameras from dropdowns
- Click **"Apply Configuration"**
- Click **"🔄 Restart Cameras"** (yellow button)

---

## 📝 Configuration Summary

**Updated config.json:**

```json
{
  "mavlink_connection": "/dev/ttyACM0:115200",  ← Direct serial
  "mavlink_auto_detect": false,
  "joystick_target": null,
  "camera": {
    "pipeline0": "udpsrc port=5000 ...",
    "pipeline1": "udpsrc port=5001 ..."
  }
}
```

---

## ✅ Checklist

Connection Setup:

- [x] Config updated to `/dev/ttyACM0:115200`
- [ ] Pixhawk USB plugged into Pi
- [ ] Pi user in dialout group
- [ ] Device shows in `ls /dev/ttyACM0`

Camera Setup:

- [x] Camera buttons now visible in GUI
- [x] Orange "Camera Settings" button prominent
- [x] Yellow "Restart Cameras" button visible
- [ ] Click Camera Settings to configure
- [ ] Detect cameras on Pi
- [ ] Select and apply configuration

---

## 🎉 Ready!

Your system is now configured for:
✅ **Direct Pixhawk serial connection** (no MAVProxy needed)
✅ **Visible camera configuration buttons** (orange & yellow)
✅ **Faster, more reliable operation**

Just connect the hardware and launch the app! 🚀
