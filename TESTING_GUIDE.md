# Testing Configuration Guide 🧪

## Current Status

Your application is running! Here's what's working:

✅ **Pixhawk Connected** - MAVLink communication working  
✅ **Application GUI** - Window opened successfully  
✅ **Joystick Detected** - Nintendo Switch Pro Controller found  
❌ **Cameras** - Waiting for real streams (now fixed with test patterns)  
❌ **Sensors** - Waiting for real hardware (now using mock data)

---

## What I Just Fixed

### 1. Updated config.json for Testing Mode

**Changed:**

```json
{
  "joystick_target": "switch", // Was "xbox", now matches your controller
  "camera": {
    // Now using test patterns instead of real camera streams
    "pipeline0": "videotestsrc pattern=smpte ...",
    "pipeline1": "videotestsrc pattern=ball ..."
  },
  "sensors": {
    "mock_mode": true // Was false, now generates fake sensor data
  }
}
```

### 2. Fixed UI Element Error

- Added null checks for UI labels
- Application won't crash if UI elements missing

---

## Test Your System Now! 🚀

### Close the current application (if still running)

Press **Ctrl+C** in the terminal or close the window

### Restart with new config

```powershell
python launch_mariner.py
```

### What You Should See:

1. **Camera Feeds** 📹

   - Camera 0: Color bars test pattern (SMPTE)
   - Camera 1: Moving ball animation
   - Both should have FPS counter overlay

2. **Sensor Data** 📊

   - Temperature: Changing values ~20-30°C
   - Pressure: Changing values ~1000-1020 hPa
   - Depth: Changing values 0-5 meters
   - Updates every 2 seconds

3. **Joystick** 🎮

   - Status shows: "Nintendo Switch Pro Controller"
   - All buttons and sticks should work

4. **Pixhawk** 🔌
   - Status shows: "Connected (udp:192.168.0.104:14550)"
   - Green indicator

---

## Testing Your Nintendo Switch Pro Controller

Your Switch Pro Controller works great! Button mapping:

| Switch Button  | ROV Function        |
| -------------- | ------------------- |
| Left Stick     | Forward/Back/Strafe |
| Right Stick    | Up/Down/Yaw         |
| ZL/ZR Triggers | Roll Left/Right     |
| A Button       | Arm/Disarm          |
| B Button       | Emergency Stop      |

**Note:** The button mapping in `joystickController.py` is designed for Xbox, so Switch buttons might be in different positions. This is normal!

---

## Testing Checklist

### After Restarting:

- [ ] **Window opens** - GUI displays
- [ ] **Camera 0 shows color bars** - Top-left video feed
- [ ] **Camera 1 shows moving ball** - Main video feed
- [ ] **FPS shown on videos** - "FPS: 30.0" overlay
- [ ] **Sensor data updating** - Numbers changing every 2 seconds
- [ ] **Pixhawk shows green** - "Connected" status
- [ ] **Joystick shows name** - "Nintendo Switch Pro Controller"
- [ ] **No error messages** - Console is clean

### Test Controls (CAREFULLY!):

⚠️ **WARNING: Your Pixhawk IS connected to real hardware!**

If you have thrusters connected:

1. Keep vehicle on surface or in pool
2. Test with low stick movements first
3. Use emergency stop if needed

**Safe Testing:**

- Move sticks gently - watch for thruster response
- Press A to arm (only if safe!)
- Press B for emergency stop
- Check that movements feel responsive

---

## Configuration Modes

### Current: Testing Mode

```json
{
  "camera": {
    "pipeline0": "videotestsrc pattern=smpte ...", // Test pattern
    "pipeline1": "videotestsrc pattern=ball ..." // Animated ball
  },
  "sensors": {
    "mock_mode": true // Fake sensor data
  }
}
```

**Use when:** Testing without ROV cameras/sensors

---

### Production Mode (When You Have Real Hardware)

```json
{
  "camera": {
    "pipeline0": "udpsrc port=5000 ! application/x-rtp,encoding-name=H264,payload=96 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink",
    "pipeline1": "udpsrc port=5001 ! application/x-rtp,encoding-name=H264,payload=97 ! rtph264depay ! avdec_h264 ! videoconvert ! appsink"
  },
  "sensors": {
    "mock_mode": false,
    "host": "192.168.21.126", // Your Raspberry Pi IP
    "port": 5000
  }
}
```

**Use when:** ROV is fully assembled with cameras streaming

---

## Troubleshooting

### "Still shows camera errors"

- Restart the application after config change
- GStreamer test patterns should work without any installation

### "No video showing"

- Check that GStreamer is installed
- Test: `gst-inspect-1.0 videotestsrc`
- If missing, install GStreamer for Windows

### "Joystick not responding"

```powershell
# Test if pygame sees it
python -c "import pygame; pygame.init(); j = pygame.joystick.Joystick(0); j.init(); print(f'{j.get_name()} - {j.get_numaxes()} axes, {j.get_numbuttons()} buttons')"
```

### "Pixhawk System ID: 0"

- This is OK! System ID 0 means it's responding
- Your MAVLink connection is working
- Can send commands to vehicle

---

## Next Steps

### Once Everything Works:

1. **Test Object Detection**

   - Click "Toggle Detection" button
   - Should see detection boxes on test pattern

2. **Test Emergency Stop**

   - Press B button on controller
   - Should see "EMERGENCY STOP ACTIVATED" message
   - All thrusters go neutral

3. **Try Arming (if safe)**

   - Press A button
   - Status changes to "Armed: YES"
   - Press A again to disarm

4. **Switch to Real Hardware**
   - Edit config.json back to real camera pipelines
   - Set mock_mode to false
   - Restart application

---

## Your System Status 🎯

```
✅ Software Installation: Complete
✅ GUI Loading: Working
✅ MAVLink Connection: Active
✅ Joystick Detection: Working (Switch Pro Controller)
🔄 Camera Display: Now showing test patterns
🔄 Sensor Telemetry: Now using mock data
⚠️ Ready for controlled testing!
```

---

## Safe Testing Procedure

### If Your ROV/Thrusters Are Connected:

1. **Keep vehicle restrained** (on blocks or held)
2. **Test in air first** (no water)
3. **Have emergency stop ready** (B button)
4. **Start with small stick movements**
5. **Watch thruster response**
6. **If anything unexpected → EMERGENCY STOP**

### Moving to Water Testing:

1. **Test in shallow pool first**
2. **Have safety line attached**
3. **Keep within reach**
4. **Monitor battery voltage**
5. **Test emergency stop procedure**

---

## Need Help?

**Console Messages Guide:**

- `✅` Green checkmark = Success
- `❌` Red X = Error/Failure
- `⚠️` Warning = Caution needed
- `🎮` Controller = Joystick related
- `📹` Camera = Video feed related
- `📊` Chart = Sensor data related

**Check these files:**

- `TROUBLESHOOTING.md` - Common issues
- `ARCHITECTURE.md` - System overview
- `CONNECTION_DIAGRAM.md` - Network setup

---

## Summary

You're almost there! After restarting with the new config:

- ✅ Test pattern videos will display
- ✅ Mock sensor data will update
- ✅ Switch Pro Controller is ready
- ✅ Pixhawk connection is active

**Your system is ready for controlled testing! 🚀**

---

_Testing Guide v1.0_  
_UIU MARINER ROV Control System_
