# 🎮 QUICK START - Your Gaming Console is Ready!

## ✅ What's Fixed

Your **Nintendo Switch Pro Controller** (or any gaming controller) now works with the ROV system!

### Changes Made:

1. ✅ **Auto-detect any controller** - No more "xbox not found" error
2. ✅ **Crash protection** - GUI won't freeze if controller has issues
3. ✅ **Better status display** - See exactly what's connected
4. ✅ **Mock sensors enabled** - Test without real hardware

---

## 🚀 How to Launch

### 1. Connect Your Controller

**Nintendo Switch Pro Controller:**

- USB: Just plug it in with USB cable
- Bluetooth: Pair it in Windows Settings

**Other Controllers:**

- Xbox: USB or Wireless Adapter
- PlayStation: USB (may need DS4Windows for Bluetooth)

### 2. Start the Application

```powershell
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

### 3. What You'll See

```
============================================================
UIU MARINER - ROV Control System
============================================================

✅ Running in virtual environment
✅ All dependencies installed

🚀 Starting application...

[JOYSTICK] Found 1 joystick(s)
[JOYSTICK] 0: Nintendo Switch Pro Controller
[JOYSTICK] ✅ Connected to: Nintendo Switch Pro Controller
[PIXHAWK] ✅ Connected
[SENSORS] ✅ Sensors: Connected
[MARINER] ✅ Application initialized successfully
```

The **GUI window** will open showing:

- 📹 Camera feeds (currently show errors - need GStreamer)
- 📊 Sensor readings (mock data for testing)
- 🎛️ Control buttons (ARM, EMERGENCY STOP, etc.)
- 📡 Status indicators (Pixhawk, Joystick, Sensors)

---

## 🎮 Controller Layout

### Left Analog Stick

- **Forward/Back** - Forward/backward movement
- **Left/Right** - Strafe left/right

### Right Analog Stick

- **Left/Right** - Yaw rotation
- **Up/Down** - Vertical up/down

### Buttons

- **A/B/X/Y** (varies by controller) - Various functions
- **Start** - Menu
- **Select** - Options

> **Note:** Button mappings may vary. Test carefully with thrusters **DISARMED**!

---

## ⚠️ Important Safety

### Before Arming Thrusters

1. ✅ Controller connected and ready
2. ✅ Pixhawk connected
3. ✅ ROV in water (thrusters must be submerged!)
4. ✅ EMERGENCY STOP button accessible
5. ✅ Test in a controlled environment first

### Testing Procedure

1. **Launch application** with thrusters **DISARMED**
2. **Move analog sticks** and verify GUI responds
3. **Check Pixhawk connection** status
4. **Only then** click **ARM THRUSTERS**
5. **Test gently** in water
6. **Press EMERGENCY STOP** if anything unexpected happens

---

## 🧪 Testing Tools

### Test Your Controller

```powershell
python test_joystick.py
```

**Shows:**

- ✅ All detected controllers
- ✅ Live stick movements
- ✅ Button presses
- ✅ D-pad input

**Use this to:**

- Verify controller works
- See controller's real name
- Test button layout

### Check System Status

```powershell
python system_check.py
```

**Verifies:**

- ✅ Python version
- ✅ All dependencies
- ✅ Config file
- ✅ Controller detection
- ✅ UI files

---

## 📹 Camera Setup (Optional)

Currently you'll see camera errors:

```
[CAM0] ❌ Failed to open: videotestsrc pattern=...
```

**Why?** Windows needs GStreamer installed.

**Fix:** See **GSTREAMER_GUIDE.md** for installation instructions.

**Good news:** Everything else works without cameras!

---

## 🔍 Troubleshooting

### Controller Not Detected

1. **Test it:**

   ```powershell
   python test_joystick.py
   ```

2. **Check Windows:**

   - Settings → Devices → Bluetooth & other devices
   - Should show your controller

3. **Try USB cable** instead of Bluetooth

### GUI Opens But Nothing Happens

1. **Check terminal output** for errors
2. **Wait 2 seconds** for controller calibration
3. **Move analog sticks** - should see response in terminal
4. **Make sure thrusters are ARMED** (click ARM button)

### Application Crashes

1. **Press Ctrl+C** to stop
2. **Run system check:**
   ```powershell
   python system_check.py
   ```
3. **Check TROUBLESHOOTING.md** for detailed help

---

## 📚 Documentation

| File                   | Description                            |
| ---------------------- | -------------------------------------- |
| **FIXES_APPLIED.md**   | Detailed explanation of what was fixed |
| **TROUBLESHOOTING.md** | Complete troubleshooting guide         |
| **QUICKSTART.md**      | Original quick start guide             |
| **README_COMPLETE.md** | Full system documentation              |
| **GSTREAMER_GUIDE.md** | Camera setup instructions              |

---

## 🎯 Next Steps

### 1. Test With Controller

```powershell
# Connect your controller first!
.\venv\Scripts\Activate.ps1
python test_joystick.py
```

Move sticks and press buttons to verify it works.

### 2. Launch Application

```powershell
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

The GUI should open with your controller detected.

### 3. Test Controls (Safely!)

- ⚠️ **Keep thrusters DISARMED for initial testing**
- Move analog sticks
- Watch the terminal output
- Verify Pixhawk connection
- Check sensor readings

### 4. When Ready for Real Hardware

Edit `config.json`:

```json
{
  "sensors": {
    "mock_mode": false,
    "host": "192.168.0.104"
  }
}
```

Then:

1. Power on ROV
2. Check network: `ping 192.168.0.104`
3. Launch application
4. **Test in water with thrusters disarmed first!**

---

## 💡 Pro Tips

### Multiple Controllers?

The system will automatically use the first one it finds. To specify:

```json
{
  "joystick_target": "switch" // or "xbox", "playstation", etc.
}
```

### Want to See Thruster Values?

Watch the terminal output - it shows control loop activity.

### Testing Without ROV?

Mock mode is enabled by default! You can test:

- ✅ Controller input
- ✅ GUI functionality
- ✅ Sensor data display
- ✅ All controls

---

## ✅ You're Ready!

**Everything is configured to work with your controller!**

Just connect it and run:

```powershell
.\venv\Scripts\Activate.ps1
python launch_mariner.py
```

---

**Need Help?**

- Run: `python system_check.py`
- See: **TROUBLESHOOTING.md**
- See: **FIXES_APPLIED.md**

---

**Last Updated:** November 4, 2025  
**Status:** ✅ Ready to use with any gaming controller!
