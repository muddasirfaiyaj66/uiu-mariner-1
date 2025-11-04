# Thruster Control Diagnosis

## ✅ Verified Working

**Ground Station → Pixhawk Communication:**

- ✅ Connection successful (`tcp:raspberrypi.local:7000`)
- ✅ Pixhawk heartbeat received
- ✅ Mode set to MANUAL successfully
- ✅ ARM command accepted by Pixhawk
- ✅ All 8 RC_CHANNELS_OVERRIDE commands transmitted successfully
- ✅ RC channel values verified: 1000-2000 range, 1500 neutral

**Test Results:**

```
[RC_OVERRIDE] Sending → Ch1-8: [1875, 1875, 1875, 1875, 1875, 1875, 1875, 1875]
✅ Sent → Forward Motion
✅ Sent → Reverse Motion
✅ Sent → Yaw Left
✅ Sent → Yaw Right
✅ Sent → Vertical Up
✅ Sent → Vertical Down
✅ Sent → All Neutral
```

---

## ❓ Why Thrusters Aren't Spinning

The RC_CHANNELS_OVERRIDE commands are reaching Pixhawk, but thrusters aren't moving. This is a **hardware/firmware configuration issue**, not a communication issue.

### Root Causes (in order of probability):

#### 1. **Pixhawk Serial Connection to Pi is Broken**

- Check Pi's serial port connection to Pixhawk
- Pixhawk RX/TX may not be connected properly
- **Test**: On Pi, check serial device:
  ```bash
  ls -l /dev/ttyAMA0  # Should exist and be readable
  ```

#### 2. **Pixhawk Firmware is NOT ArduSub**

- Wrong firmware (e.g., ArduPlane, ArduCopter)
- ArduSub is required for underwater 8-thruster control
- **Test**: Check firmware version on Pixhawk, should show "ArduSub" in boot screen

#### 3. **ESCs Not Armed**

- ESCs need to be armed before responding to PWM
- Usually indicated by **red LED on Pi** (not blue/green)
- **Fix**: Power cycle the Pi/Pixhawk system
  - Disconnect power from Pixhawk
  - Wait 10 seconds
  - Reconnect power
  - Wait for red/solid color LED (ESCs armed)

#### 4. **RC Channel Mapping Wrong**

- Pixhawk channels 1-8 may not be mapped to physical thrusters
- **Test**: In Mission Planner (on ground station or remotely):
  1. Connect via MAVLink to Pixhawk
  2. Go to Setup → Radio Calibration
  3. Move thrusters in Mission Planner and watch sliders
  4. Verify all 8 channels move when commands sent

#### 5. **Thruster Motor Connections**

- Motor connectors may be loose
- Thruster ESCs may not be receiving 5V servo power
- **Test**:
  - Check all 8 ESC servo connectors to Pixhawk (should be tight)
  - Check voltage on servo rail (should be ~5V)

#### 6. **Motor Rotation Direction**

- Thrusters may be programmed to rotate backwards
- Test by manually spinning motor (should go forward for positive PWM)
- **Fix**: In Mission Planner, reverse motor directions if needed

---

## Next Steps: Verify Hardware

### On the Raspberry Pi

```bash
# 1. Check serial port connection to Pixhawk
ssh pi@raspberrypi.local
ls -l /dev/ttyAMA0

# 2. Check if data is actually flowing on the serial port
cat /dev/ttyAMA0 &  # Should show MAVLink messages
# Ctrl+C to stop
```

### Power/Status Indicators

**Check LED status on Pi:**

- **Blue LED blinking** = Pixhawk is powered, not armed
- **Red LED solid** = ESCs armed, ready
- **No LED** = Power issue

**If no red LED:**

1. Disconnect power
2. Wait 10 seconds
3. Reconnect power
4. Wait 30 seconds for Pixhawk boot
5. Red LED should appear

### Pixhawk Firmware Check

Connect via Mission Planner and check:

1. **Setup** → **Planner**
2. Look at "Frame" setting - should be 8-thruster configuration
3. Look at "Firmware Version" - should mention "ArduSub"

---

## Testing Thruster Response

### Method 1: Direct Serial Monitoring (on Pi)

```bash
ssh pi@raspberrypi.local "python3 -c \"
import serial
ser = serial.Serial('/dev/ttyAMA0', 57600, timeout=1)
while True:
    data = ser.read(300)
    if data and b'HEARTBEAT' not in data:
        print('Got RC data:', len(data), 'bytes')
\" &"
```

### Method 2: Mission Planner Test

If you have Mission Planner installed on another PC:

1. Connect via **Add Link** → TCP
2. Connect to `raspberrypi.local:7000`
3. Go to **Servos** tab
4. Look at output values moving

---

## Quick Fixes to Try (in order)

### 1️⃣ Power Cycle Everything

```bash
# On Pi
ssh pi@raspberrypi.local "sudo shutdown -h now"
# Wait 30 seconds, power back on
# Wait another 30 seconds for boot
```

### 2️⃣ Check Physical Connections

- All 8 ESC servo connectors to Pixhawk firmly seated
- Power connector to Pixhawk firmly seated
- All motor connectors to ESCs firmly seated

### 3️⃣ Verify Serial Port Baud Rate

In `config.json`:

```json
{
  "serial_baud": 57600 // Should match Pixhawk (usually 57600 or 115200)
}
```

### 4️⃣ Check Pixhawk Parameter: RC_PROTOCOLS

- Should be set to "2: MAVLink2" or "1: MAVLink1"
- NOT "0: Disabled"

---

## Status Summary

| Component                   | Status     | Notes                            |
| --------------------------- | ---------- | -------------------------------- |
| Ground Station ↔ Pi Network | ✅ Working | TCP connection stable            |
| Pi ↔ Pixhawk Serial         | ❓ Unknown | Need to verify                   |
| Pixhawk Command Receipt     | ✅ Working | RC_CHANNELS_OVERRIDE accepted    |
| Pixhawk → ESC PWM Output    | ❓ Unknown | Need to verify with scope or LED |
| ESC → Motor Control         | ❓ Unknown | Dependent on ESC arming          |
| Motor Rotation              | ❓ Unknown | Not verified yet                 |

---

## How to Use the Test Script Going Forward

To repeat the thruster test:

```bash
cd F:\Web Development\uiu-mariner\uiu-mariner-1
python test_thruster_arm_and_spin.py
```

This will:

1. Connect to Pixhawk
2. Set MANUAL mode
3. ARM thrusters
4. Send 75% forward command to all thrusters
5. Test individual directions (forward, reverse, yaw, vertical)
6. DISARM
7. Report success/failure

---

## Questions for Debugging

When you test, check:

1. Do any LEDs on the Pi light up when you run the test?
2. Do any motor/thruster beeps occur?
3. Can you manually spin thrusters by hand (should be hard if ESCs charged)?
4. What do the status LEDs show (color, solid, blinking)?

Let me know the answers and I can help diagnose further!
