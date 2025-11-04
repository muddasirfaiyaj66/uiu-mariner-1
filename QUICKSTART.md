# UIU MARINER - Quick Start Guide 🚀

## ⚠️ IMPORTANT: Where to Run This Software

**This is GROUND STATION software - runs on YOUR PC (Windows), not on the ROV!**

```
Ground Station PC (This Software)  ←→  Network  ←→  ROV (Raspberry Pi + Pixhawk)
- Xbox Controller connects HERE         WiFi/Ethernet     - Cameras
- Displays camera feeds                                    - Sensors
- Shows sensor data                                        - Pixhawk
- Sends thruster commands                                  - Thrusters
```

See `ARCHITECTURE.md` for complete system overview.

---

## Get Running in 5 Minutes!

### Step 1: Setup Virtual Environment (Recommended)

**PowerShell:**

```powershell
.\setup.ps1
```

**Command Prompt:**

```cmd
setup.bat
```

This will automatically:

- ✅ Create virtual environment
- ✅ Activate it
- ✅ Install all dependencies

**OR Manual Installation (without virtual environment):**

```powershell
pip install -r requirements.txt
```

**What gets installed:**

- PyQt6 (GUI)
- pymavlink (Pixhawk communication over network)
- pygame (Joystick - Xbox controller)
- opencv-python (Camera video display)
- numpy (Math operations)

---

### Step 2: Connect Hardware (Ground Station PC)

#### Xbox Controller → YOUR PC

**Connect joystick to Ground Station (this PC), NOT to ROV!**

**Option A: USB Cable (Recommended)**

1. Plug Xbox controller USB cable into your PC
2. Windows automatically installs drivers
3. Test: Settings → Devices → "Set up USB game controllers"

**Option B: Bluetooth Wireless**

1. Turn on Xbox controller (hold Xbox button)
2. Hold pairing button until light flashes
3. PC: Settings → Bluetooth → Add Device
4. Select "Xbox Wireless Controller"

#### ROV Network Connection

**Your PC must be on same network as ROV:**

Set your PC's IP to: `192.168.0.100`

- ROV should be at: `192.168.0.104`
- Control Panel → Network → Change adapter settings
- Right-click Ethernet/WiFi → Properties → IPv4

**Test connection:**

````powershell
ping 192.168.0.104
# Should get replies!

---

### Step 3: Configure

Edit `config.json` with your settings:

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "joystick_target": "xbox",
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  },
  "sensors": {
    "host": "192.168.21.126",
    "port": 5000,
    "protocol": "tcp",
    "mock_mode": false
  }
}
````

**Testing without hardware?** Set `"mock_mode": true`

---

### Step 4: Launch!

```powershell
python launch_mariner.py
```

Or directly:

```powershell
python src/ui/marinerApp.py
```

---

## First Time Checklist ✅

Before diving:

1. **Camera Feeds** 📹

   - [ ] See video from both cameras?
   - [ ] FPS counter showing (top-left)?
   - [ ] If not: Enable mock_mode or check GStreamer

2. **Sensor Data** 📊

   - [ ] Temperature, pressure, depth updating?
   - [ ] If not: Enable mock_mode or check TCP connection

3. **Pixhawk Connection** 🔌

   - [ ] Status shows "Connected" in green?
   - [ ] If not: Check IP address and ping ROV

4. **Joystick** 🎮
   - [ ] Status shows your controller name?
   - [ ] If not: Reconnect and restart app

---

## Quick Controls 🎮

### Xbox Controller

| Button      | Action                       |
| ----------- | ---------------------------- |
| Left Stick  | Move forward/back/left/right |
| Right Stick | Up/down + rotate             |
| Triggers    | Roll left/right              |
| A           | Arm/Disarm                   |
| B           | Emergency Stop               |

### GUI Buttons

- **ARM THRUSTERS** - Enable motors (⚠️ CAUTION!)
- **EMERGENCY STOP** - Instant neutral + disarm
- **Toggle Detection** - Turn object detection on/off

---

## Testing Without Hardware 🧪

1. Edit `config.json`:

```json
{
  "sensors": {
    "mock_mode": true
  },
  "camera": {
    "pipeline0": "videotestsrc ! videoconvert ! appsink",
    "pipeline1": "videotestsrc pattern=ball ! videoconvert ! appsink"
  }
}
```

2. Launch normally - you'll see:
   - Test pattern videos
   - Mock sensor data (changing values)
   - Full GUI functionality

---

## Common Issues & Fixes 🔧

### "Pixhawk not connected"

```powershell
# Test network
ping 192.168.0.104

# Check if MAVLink port is open
Test-NetConnection -ComputerName 192.168.0.104 -Port 14550
```

### "No camera feed"

1. Check GStreamer: `gst-inspect-1.0 --version`
2. Enable mock cameras (see Testing section above)
3. Verify Pi is streaming to ports 5000/5001

### "Joystick not detected"

1. Reconnect controller
2. Restart application
3. Test in Windows game controllers

### "Import errors"

```powershell
# Reinstall everything
pip install -r requirements.txt --force-reinstall

# Or use virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Safety First! ⚠️

### BEFORE Operating:

1. ✅ Test on surface first
2. ✅ Verify emergency stop works
3. ✅ Check all thrusters neutral
4. ✅ Have spotter/safety person
5. ✅ Know your exit plan

### DURING Operation:

- 👀 Monitor battery voltage
- 👀 Watch for error messages
- 👀 Keep emergency stop accessible
- 👀 Stay within safe depth limits

### IF EMERGENCY:

1. Press **B button** or **Emergency Stop**
2. Thrusters → neutral
3. Vehicle → disarmed
4. Surface immediately if needed

---

## What's Next? 📚

✅ **Got it working?** Read the full docs:

- `README_COMPLETE.md` - Complete guide
- `SYSTEM_OVERVIEW.md` - Technical details
- `docs/TROUBLESHOOTING.md` - More solutions

🎯 **Ready to customize?**

- Edit `main_window.ui` in Qt Designer
- Modify `config.json` for your setup
- Adjust detection in `cameraWorker.py`

🚀 **Want to contribute?**

- Add YOLO detection
- Improve UI/UX
- Test and report issues

---

## File Locations 📂

```
mariner-software-1.0/
├── launch_mariner.py          ← Start here!
├── config.json                ← Your settings
├── requirements.txt           ← Dependencies
├── QUICKSTART.md             ← This file
└── src/
    └── ui/
        └── marinerApp.py      ← Main application
```

---

## Support 💬

**Status Indicators in GUI:**

- 🟢 Green = Connected/OK
- 🟠 Orange = Standby/Unarmed
- 🔴 Red = Error/Disconnected

**Need help?**

1. Check error message in console
2. Review troubleshooting section above
3. Read full documentation
4. Check hardware connections

---

## You're Ready! 🌊

```
┌─────────────────────────────────────┐
│  UIU MARINER ROV Control System     │
│  Status: Ready to Dive              │
│                                     │
│  📹 Cameras: Active                 │
│  🎮 Controller: Connected           │
│  🔌 Pixhawk: Online                 │
│  📊 Sensors: Reading                │
│                                     │
│  ⚠️  REMEMBER: SAFETY FIRST!       │
└─────────────────────────────────────┘
```

**Happy exploring! 🤖**

---

_Quick Start Guide v1.0_  
_For complete documentation, see README_COMPLETE.md_
