# 🔧 THRUSTER NOT WORKING - TROUBLESHOOTING GUIDE

## Problem

The test shows all components working (joystick, MAVLink connection, commands being sent), but thrusters don't actually move.

## Diagnostic Results

- ✅ Joystick working
- ✅ PWM conversion correct
- ✅ Pixhawk connection established
- ✅ RC_CHANNELS_OVERRIDE messages sent
- ⚠️ Connection unstable (frequent EOF errors)
- ❓ Unknown if Pixhawk is armed/mode/outputting PWM

---

## Most Likely Causes (in order)

### 1. ⚠️ **Pixhawk is DISARMED**

**Most common issue!** Pixhawk will NOT output PWM to thrusters unless armed.

**Fix on Raspberry Pi:**

```bash
ssh pi@raspberrypi.local
python3 ~/mariner/pi_scripts/test_arm_pixhawk.py
```

Or use QGroundControl to arm manually.

---

### 2. 🔌 **Pixhawk in wrong flight mode**

ArduSub needs to be in **STABILIZE** or **MANUAL** mode for RC_CHANNELS_OVERRIDE to work.

**Check mode on Pi:**

```bash
ssh pi@raspberrypi.local
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200
# In MAVProxy console:
mode STABILIZE
arm throttle
```

---

### 3. 🛡️ **Safety Switch Enabled**

Some Pixhawk boards require a physical safety switch to be pressed before arming.

**Solutions:**

- Press the safety switch button on Pixhawk (if present)
- Disable via parameter: `BRD_SAFETY_DEFLT = 0`

**On Pi via MAVProxy:**

```bash
mavproxy.py --master=/dev/ttyACM0
# In console:
param set BRD_SAFETY_DEFLT 0
```

---

### 4. ⚡ **ESCs Not Powered or Calibrated**

ESCs need power and must be calibrated to accept PWM signals.

**Check:**

- Battery connected and charged (>11V)
- ESC power LED lights on
- ESCs make initialization beeps

**Calibrate ESCs:**

1. In QGroundControl: Vehicle Setup → Motors
2. Follow ESC calibration wizard
3. Or manually: Send 2000μs to all channels, power on ESCs, then send 1000μs

---

### 5. 📊 **Pixhawk Parameters Wrong**

Critical parameters might be misconfigured.

**Check these parameters (via QGroundControl or MAVProxy):**

```
MOT_PWM_MIN = 1100   (or 1000)
MOT_PWM_MAX = 1900   (or 2000)
FRAME_CONFIG = 1     (1 = BlueROV2, 0 = Custom)
ARMING_CHECK = 1     (enable all safety checks)
```

---

### 6. 🌐 **MAVProxy Server Crashing**

The frequent "EOF on TCP socket" suggests MAVProxy is unstable.

**Restart MAVProxy on Pi:**

```bash
ssh pi@raspberrypi.local
sudo systemctl restart mavproxy
# Or manually:
pkill mavproxy
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

---

### 7. 🔧 **Pixhawk Not Receiving Commands**

RC_CHANNELS_OVERRIDE might not be accepted.

**Check:**

- System ID matches (default 1)
- Component ID correct
- RC failsafe not triggered

---

## Quick Test on Raspberry Pi

Run this directly on the Pi to bypass network issues:

```bash
ssh pi@raspberrypi.local
cd ~/mariner/pi_scripts

# 1. Check Pixhawk connection
python3 detect_pixhawk.py

# 2. Test arming
python3 test_arm_pixhawk.py

# 3. Test thruster direct (CAREFUL!)
python3 -c "
from pymavlink import mavutil
master = mavutil.mavlink_connection('/dev/ttyACM0', baud=115200)
master.wait_heartbeat()
print('Connected!')

# Arm
master.arducopter_arm()
master.motors_armed_wait()
print('Armed!')

# Test Ch1 = 1600 (slight forward)
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    1600, 1500, 1500, 1500, 1500, 1500, 1500, 1500
)
print('Command sent - thruster 1 should spin')

import time
time.sleep(3)

# Return to neutral
master.mav.rc_channels_override_send(
    master.target_system,
    master.target_component,
    1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500
)

# Disarm
master.arducopter_disarm()
print('Disarmed')
"
```

---

## Use QGroundControl for Diagnosis

1. Connect QGC to Pixhawk (via Raspberry Pi)
2. Check:
   - Vehicle Setup → Summary → Firmware version
   - Vehicle Setup → Motors → Test motors individually
   - Analyze Tools → MAVLink Inspector → See RC_CHANNELS_OVERRIDE
   - Fly View → Check armed status and mode

---

## Action Plan

### Step 1: Check Basic Setup

```bash
# On Raspberry Pi
ssh pi@raspberrypi.local

# Check MAVProxy is running
ps aux | grep mavproxy

# If not running, start it:
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &
```

### Step 2: Arm the Pixhawk

```bash
# On Pi
python3 ~/mariner/pi_scripts/test_arm_pixhawk.py
```

### Step 3: Test Again from Windows

```powershell
# On Windows
python test_thruster_dataflow.py
# When prompted for live test, say YES
```

### Step 4: If Still Not Working

- Use QGroundControl to manually test motors
- Check ESC power and calibration
- Verify battery voltage
- Check physical wiring

---

## Preventive Measures

### Make Pixhawk Stay Armed

Add this to your main control script:

```python
# Check and re-arm if needed
def ensure_armed(pixhawk):
    status = pixhawk.vehicle.recv_match(type='HEARTBEAT', blocking=False)
    if status and not (status.base_mode & 128):  # Not armed
        print("[AUTO-ARM] Re-arming Pixhawk...")
        pixhawk.arm()
```

### Stable MAVProxy Service

On Pi, create `/etc/systemd/system/mavproxy.service`:

```ini
[Unit]
Description=MAVProxy for Pixhawk
After=network.target

[Service]
Type=simple
User=pi
ExecStart=/usr/local/bin/mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl enable mavproxy
sudo systemctl start mavproxy
```

---

## Next Steps

1. **SSH to Pi and check if Pixhawk is armed**
2. **Use QGroundControl to verify motor outputs**
3. **Check ESC power and calibration**
4. **Test one thruster at a time**

---

## Contact Info

If none of these work, the issue is likely:

- Hardware (wiring, power, ESC failure)
- Firmware (wrong ArduSub version)
- Parameter corruption (reset to defaults)
