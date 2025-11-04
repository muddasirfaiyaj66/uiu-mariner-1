# 🎯 NEXT STEPS - Thruster Troubleshooting

## Current Situation

Your test results show:

- ✅ **Joystick working** - Nintendo Switch Pro Controller detected and reading correctly
- ✅ **PWM conversion correct** - Axis values converting to proper 1000-2000μs range
- ✅ **Pixhawk connection established** - MAVLink connects successfully
- ✅ **Commands being sent** - RC_CHANNELS_OVERRIDE messages sent without errors
- ❌ **Thrusters not moving** - Physical thrusters don't respond
- ⚠️ **Connection unstable** - Frequent "EOF on TCP socket" errors

## Why Thrusters Aren't Moving

Based on the diagnostics, the most likely causes are:

### 1. **Pixhawk is DISARMED** ⭐ Most Likely!

The Pixhawk must be armed before it will output PWM to the ESCs/thrusters.

### 2. **Wrong Flight Mode**

ArduSub needs to be in STABILIZE or MANUAL mode for RC_CHANNELS_OVERRIDE.

### 3. **ESCs Not Powered**

ESCs need separate power from a battery to spin the motors.

### 4. **Safety Switch Required**

Some Pixhawk boards need a physical safety button pressed.

---

## 🚀 Action Plan

### Option A: Test on Raspberry Pi (RECOMMENDED)

This bypasses all network issues and tests the hardware directly.

**Step 1: Run the direct test**

```powershell
# On Windows
.\test_thruster_on_pi.ps1
```

This will:

- Upload `test_thruster_direct.py` to the Pi
- Run it directly on the Pi
- Test each thruster channel one by one
- Show you servo outputs in real-time

**What this tells you:**

- ✅ If thrusters spin → Hardware is fine, problem is Windows↔Pi connection
- ❌ If thrusters don't spin → Hardware issue (power, calibration, wiring)

---

### Option B: Use QGroundControl

QGroundControl has built-in motor testing that bypasses all your code.

**Step 1: Install QGroundControl**

- Download from: https://qgroundcontrol.com/

**Step 2: Connect to Pixhawk**

- Connect via: TCP → raspberrypi.local:5760

**Step 3: Test Motors**

1. Go to: Vehicle Setup → Motors
2. Remove propellers!
3. Click "Test All Motors"
4. Each thruster will spin briefly

**What this tells you:**

- ✅ If motors spin → Pixhawk and ESCs work fine
- ❌ If motors don't spin → ESC power/calibration issue

---

### Option C: Manual Arming via SSH

The simplest fix - just arm the Pixhawk!

**Step 1: SSH to Pi**

```powershell
ssh pi@raspberrypi.local
```

**Step 2: Run MAVProxy**

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
```

**Step 3: In MAVProxy console:**

```
mode STABILIZE
arm throttle
```

**Step 4: Keep MAVProxy running, go back to Windows and run:**

```powershell
python test_thruster_dataflow.py
```

---

## 🔍 Diagnostic Commands

### Check if Pixhawk is Connected (on Pi)

```bash
ls -la /dev/tty* | grep ACM
# Should show: /dev/ttyACM0
```

### Check if MAVProxy is Running (on Pi)

```bash
ps aux | grep mavproxy
```

### Check Pixhawk Status (on Pi)

```bash
cd ~/mariner/pi_scripts
python3 test_arm_pixhawk.py
```

### Test Single Thruster (on Pi)

```bash
python3 -c "
from pymavlink import mavutil
m = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
m.wait_heartbeat()
print('Connected')
m.arducopter_arm()
m.motors_armed_wait()
print('Armed')
m.mav.rc_channels_override_send(m.target_system, m.target_component, 1600, 1500, 1500, 1500, 1500, 1500, 1500, 1500)
import time
time.sleep(3)
m.mav.rc_channels_override_send(m.target_system, m.target_component, 1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500)
m.arducopter_disarm()
print('Done')
"
```

---

## 🔧 Common Fixes

### Fix 1: Restart MAVProxy

```bash
# On Pi
sudo pkill mavproxy
sleep 2
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &
```

### Fix 2: Disable Safety Switch

```bash
# On Pi in MAVProxy console
param set BRD_SAFETY_DEFLT 0
param set ARMING_CHECK 0  # Disable all safety checks (testing only!)
```

### Fix 3: Check ESC Calibration

```bash
# In QGroundControl:
# Vehicle Setup → Motors → Calibrate ESCs
```

### Fix 4: Check Battery Voltage

```bash
# In MAVProxy console (on Pi)
status
# Look for: battery: XX.XVolt
# Should be > 11V for proper ESC operation
```

---

## 📊 Expected Behaviors

### When Everything Works:

```
[CONNECT] Attempting to connect → tcp:raspberrypi.local:7000
[✅] Heartbeat received — Pixhawk Connected!
[✅] Thrusters armed!
   Sending commands...
   (Thrusters spin based on joystick input)
```

### When Pixhawk is Disarmed:

```
[✅] Heartbeat received — Pixhawk Connected!
[❌] Thrusters disarmed
   Sending commands...
   (Nothing happens - thrusters stay still)
```

### When ESCs Not Powered:

```
[✅] Heartbeat received — Pixhawk Connected!
[✅] Thrusters armed!
   Sending commands...
   (No sound, no movement, ESC LEDs off)
```

---

## 🎯 Your Next Command

**Run this now to test directly on Pi:**

```powershell
.\test_thruster_on_pi.ps1
```

This will definitively tell you if the issue is:

- ✅ **Software/Network** - Can be fixed by improving connection handling
- ❌ **Hardware** - Needs physical intervention (power, wiring, calibration)

---

## 📖 Additional Resources

- **Full troubleshooting guide**: `THRUSTER_NOT_WORKING_FIXES.md`
- **Test scripts**: `pi_scripts/test_thruster_direct.py`
- **Connection docs**: `CONNECTION_ARCHITECTURE.md`
- **Hardware guide**: `CONNECT_HARDWARE_GUIDE.md`

---

## Need More Help?

If thrusters still don't work after trying all the above:

1. **Take photos/video of:**

   - Pixhawk LED status
   - ESC LED status
   - Battery voltage display
   - Wiring connections

2. **Collect logs:**

   ```bash
   # On Pi
   dmesg | tail -50 > pixhawk_logs.txt
   ```

3. **Check ArduSub firmware:**
   - In QGroundControl: Vehicle Setup → Summary
   - Should be: ArduSub V4.x.x

---

**Good luck! The hardware test should reveal the root cause.** 🚀
