# 🔍 Thruster Button Data Flow - Complete Guide

## Overview

This guide explains **exactly** how pressing your thruster button (joystick) passes values through your system to power the Pixhawk MAIN OUT pins (1-8).

---

## 🎯 The Complete Data Flow

### Step 1: **Joystick Button/Axis Press**

```
📌 YOU PRESS: Left stick forward, Right stick up
```

**Hardware:** Xbox 360 Controller (or compatible)

- Connected via USB to your PC
- Windows recognizes it as a HID (Human Interface Device)

---

### Step 2: **pygame Library Reads Input**

```python
# Location: src/controllers/joystickController.py (line 167-193)

pygame.event.pump()  # Update pygame's internal state

# Read axes (analog sticks)
left_x = joystick.get_axis(0)    # -1.0 to 1.0 (left/right)
left_y = joystick.get_axis(1)    # -1.0 to 1.0 (up/down)
right_x = joystick.get_axis(3)   # -1.0 to 1.0 (left/right)
right_y = joystick.get_axis(4)   # -1.0 to 1.0 (up/down)

# Read buttons (digital on/off)
button_a = joystick.get_button(0)  # True or False
button_start = joystick.get_button(7)  # Emergency stop
```

**Example Values:**

- Left stick forward (80%): `left_y = -0.8`
- Right stick up (50%): `right_y = -0.5`
- Start button: `False`

---

### Step 3: **Deadzone Applied**

```python
# Location: src/controllers/joystickController.py (line 97-125)

DEADZONE = 0.03  # Ignore movements < 3%

if abs(value) < DEADZONE:
    return 0.0  # Ignore small movements
```

**Purpose:** Prevents thruster drift from controller noise

---

### Step 4: **Convert Axis to PWM**

```python
# Location: src/controllers/joystickController.py (line 148-163)

def axis_to_pwm(self, axis_value: float) -> int:
    """
    Convert -1.0...1.0 to 1000-2000 PWM microseconds

    Formula: PWM = 1500 + (axis_value × 500)
    """
    pwm = 1500 + int(axis_value * 500)
    return max(1000, min(2000, pwm))  # Clamp to safe range
```

**Example Conversions:**
| Axis Value | Calculation | PWM Output |
|------------|-------------|------------|
| -1.0 (full back) | 1500 + (-1.0 × 500) | 1000μs |
| -0.5 (half back) | 1500 + (-0.5 × 500) | 1250μs |
| 0.0 (neutral) | 1500 + (0.0 × 500) | 1500μs |
| +0.5 (half forward) | 1500 + (0.5 × 500) | 1750μs |
| +1.0 (full forward) | 1500 + (1.0 × 500) | 2000μs |

---

### Step 5: **Compute Thruster Channels**

```python
# Location: src/controllers/joystickController.py (line 253-317)

def compute_thruster_channels(self, joystick_state: Dict) -> List[int]:
    """
    Map joystick axes to 8 thruster channels based on ROV geometry
    """
    channels = [1500] * 8  # Start all neutral

    # Extract values
    forward_back = -axes["left_y"]   # Forward is negative
    left_right = axes["left_x"]      # Right is positive
    up_down = -axes["right_y"]       # Up is negative

    # FORWARD/BACKWARD: Channels 1 & 8
    if abs(forward_back) > 0:
        channels[0] = axis_to_pwm(forward_back)    # Ch1 (Pin 1)
        channels[7] = axis_to_pwm(-forward_back)   # Ch8 (Pin 8)

    # LEFT/RIGHT ROTATION: Channels 2 & 5
    if abs(left_right) > 0:
        channels[1] = axis_to_pwm(left_right)      # Ch2 (Pin 2)
        channels[4] = axis_to_pwm(-left_right)     # Ch5 (Pin 5)

    # UP/DOWN: Channels 3, 4, 6, 7
    if abs(up_down) > 0:
        channels[2] = axis_to_pwm(-up_down)        # Ch3 (Pin 3)
        channels[3] = axis_to_pwm(-up_down)        # Ch4 (Pin 4)
        channels[5] = axis_to_pwm(up_down)         # Ch6 (Pin 6)
        channels[6] = axis_to_pwm(up_down)         # Ch7 (Pin 7)

    return channels  # [ch1, ch2, ch3, ch4, ch5, ch6, ch7, ch8]
```

**Example Output:**

```python
# Left stick forward (80%), Right stick up (50%)
channels = [1900, 1500, 1250, 1250, 1500, 1750, 1750, 1100]
#          ^^^^ ^^^^ ^^^^ ^^^^ ^^^^ ^^^^ ^^^^ ^^^^
#          Ch1  Ch2  Ch3  Ch4  Ch5  Ch6  Ch7  Ch8
#          Pin1 Pin2 Pin3 Pin4 Pin5 Pin6 Pin7 Pin8
```

---

### Step 6: **Build MAVLink Message**

```python
# Location: src/connections/mavlinkConnection.py (line 194-239)

def send_rc_channels_override(self, channels):
    """
    Send RC_CHANNELS_OVERRIDE MAVLink message
    """
    # Validate
    if len(channels) != 8:
        print(f"❌ Expected 8 channels, got {len(channels)}")
        return False

    # Clamp to safe range
    channels = [max(1000, min(2000, int(ch))) for ch in channels]

    # Send MAVLink message
    vehicle.mav.rc_channels_override_send(
        vehicle.target_system,      # Pixhawk system ID (usually 1)
        vehicle.target_component,   # Component ID (usually 1)
        channels[0],  # Channel 1 (Pin 1)
        channels[1],  # Channel 2 (Pin 2)
        channels[2],  # Channel 3 (Pin 3)
        channels[3],  # Channel 4 (Pin 4)
        channels[4],  # Channel 5 (Pin 5)
        channels[5],  # Channel 6 (Pin 6)
        channels[6],  # Channel 7 (Pin 7)
        channels[7]   # Channel 8 (Pin 8)
    )
```

**MAVLink Message Structure:**

```
RC_CHANNELS_OVERRIDE
├─ target_system: 1
├─ target_component: 1
├─ chan1_raw: 1900  (Pin 1 - Forward thruster)
├─ chan2_raw: 1500  (Pin 2 - Rotation)
├─ chan3_raw: 1250  (Pin 3 - Vertical)
├─ chan4_raw: 1250  (Pin 4 - Vertical)
├─ chan5_raw: 1500  (Pin 5 - Rotation)
├─ chan6_raw: 1750  (Pin 6 - Vertical)
├─ chan7_raw: 1750  (Pin 7 - Vertical)
└─ chan8_raw: 1100  (Pin 8 - Forward thruster)
```

---

### Step 7: **Send Over Network**

```
📌 NETWORK PATH:
Your PC → Ethernet/WiFi → Raspberry Pi
```

**Connection String:** `tcp:raspberrypi.local:7000`

**Protocol:**

- TCP socket connection
- Port 7000 (MAVProxy server)
- Binary MAVLink v2 protocol
- Packet size: ~22 bytes per RC_CHANNELS_OVERRIDE message

---

### Step 8: **MAVProxy Relay**

```
📌 RASPBERRY PI: MAVProxy Server
Location: Port 7000 (TCP)
```

**What MAVProxy Does:**

1. Receives MAVLink messages from network (port 7000)
2. Forwards to Pixhawk via UART/USB
3. Acts as a "bridge" between network and serial

**Common MAVProxy Connection:**

```bash
mavproxy.py --master=/dev/ttyACM0 --baudrate=57600 --out=tcpin:0.0.0.0:7000
```

---

### Step 9: **Pixhawk Receives Message**

```
📌 PIXHAWK: ArduSub Firmware
Connection: UART/USB from Raspberry Pi
Baud Rate: 57600 or 115200
```

**Pixhawk Processing:**

1. **Parse MAVLink:** Decode RC_CHANNELS_OVERRIDE message
2. **Check Armed State:** Only process if armed
3. **Flight Mode:** Apply MANUAL/STABILIZE mode logic
4. **Motor Mixer:** Convert 8 channels → thruster outputs
5. **Safety Checks:** Pre-arm checks, failsafes
6. **PWM Generation:** Output PWM signals

---

### Step 10: **PWM Output to MAIN OUT Pins**

```
📌 PIXHAWK MAIN OUT (Servo Rail)
Physical pins on Pixhawk controller
```

**Pin Mapping:**

```
┌─────────────────────────────────────┐
│  PIXHAWK MAIN OUT (Back of board)  │
├──────┬──────┬──────┬──────┬────────┤
│ Pin1 │ Pin2 │ Pin3 │ Pin4 │ Pin5   │ ...
│ GND  │ GND  │ GND  │ GND  │ GND    │
│ VCC  │ VCC  │ VCC  │ VCC  │ VCC    │
│ SIG  │ SIG  │ SIG  │ SIG  │ SIG    │
└──────┴──────┴──────┴──────┴────────┘
  ↓      ↓      ↓      ↓      ↓
  1900μs 1500μs 1250μs 1250μs 1500μs
```

**Signal Characteristics:**

- **Type:** PWM (Pulse Width Modulation)
- **Voltage:** 3.3V or 5V logic level
- **Frequency:** 50Hz (20ms period)
- **Pulse Width:** 1000-2000 microseconds

---

### Step 11: **ESC Interprets PWM**

```
📌 ESC (Electronic Speed Controller)
Connects between Pixhawk and thruster motor
```

**ESC Processing:**

```
PWM Input → ESC Logic → Motor Power Output

1000μs → Full Reverse → Motor spins CCW (max speed)
1500μs → Neutral     → Motor stopped
2000μs → Full Forward → Motor spins CW (max speed)
```

**ESC Calibration:**

- Min throttle: 1000μs
- Max throttle: 2000μs
- Deadband: 1475-1525μs (stop zone)

---

### Step 12: **Thruster Motor Spins**

```
📌 THRUSTER: Brushless Motor
3-phase BLDC motor with propeller
```

**Power Flow:**

```
Battery (14.8V LiPo) → ESC → 3-Phase AC → Motor Coils → Shaft Rotation
```

**Speed Control:**

- PWM 1000μs → 100% reverse thrust
- PWM 1500μs → 0% thrust (stopped)
- PWM 2000μs → 100% forward thrust

---

## 🎮 Channel to Pin Mapping

| Channel | Pin        | Function           | Stick   | Direction                     |
| ------- | ---------- | ------------------ | ------- | ----------------------------- |
| Ch1     | MAIN OUT 1 | Forward/Back (ACW) | Left Y  | Forward: 2000μs, Back: 1000μs |
| Ch2     | MAIN OUT 2 | Rotation Left      | Left X  | Right: 2000μs, Left: 1000μs   |
| Ch3     | MAIN OUT 3 | Vertical (ACW)     | Right Y | Up: 1000μs, Down: 2000μs      |
| Ch4     | MAIN OUT 4 | Vertical (ACW)     | Right Y | Up: 1000μs, Down: 2000μs      |
| Ch5     | MAIN OUT 5 | Rotation Right     | Left X  | Right: 1000μs, Left: 2000μs   |
| Ch6     | MAIN OUT 6 | Vertical (CW)      | Right Y | Up: 2000μs, Down: 1000μs      |
| Ch7     | MAIN OUT 7 | Vertical (CW)      | Right Y | Up: 2000μs, Down: 1000μs      |
| Ch8     | MAIN OUT 8 | Forward/Back (CW)  | Left Y  | Forward: 1000μs, Back: 2000μs |

---

## ⚡ Timing and Latency

**Total Latency:** ~50-100ms (end-to-end)

| Stage                | Time    | Notes                  |
| -------------------- | ------- | ---------------------- |
| Joystick read        | 1-5ms   | USB polling rate       |
| PWM conversion       | <1ms    | Simple calculation     |
| MAVLink encode       | <1ms    | Message packing        |
| Network transmission | 5-20ms  | TCP over Ethernet      |
| MAVProxy relay       | 1-5ms   | UART forwarding        |
| Pixhawk processing   | 10-20ms | Flight controller loop |
| PWM output           | 20ms    | 50Hz signal period     |
| ESC response         | 10-30ms | ESC refresh rate       |

**Control Loop Frequency:** 10Hz (100ms interval)

- Location: `src/ui/marinerApp.py` line 1041
- Timer interval: 100ms
- Configurable in `config.json` → `update_rate_hz`

---

## 🔧 Testing the Data Flow

### Test 1: Run Diagnostic Script

```powershell
.\diagnose_thruster_flow.ps1
```

Checks:

- ✅ Python environment
- ✅ Required packages
- ✅ Joystick detection
- ✅ Network to Pi
- ✅ MAVProxy port
- ✅ Config file

---

### Test 2: Run Complete Data Flow Test

```bash
python test_thruster_dataflow.py
```

Tests:

1. Joystick detection
2. Joystick input reading
3. PWM conversion
4. Pixhawk connection
5. MAVLink message sending
6. **Live thruster control** (interactive)

---

### Test 3: Monitor in QGroundControl

**Setup:**

1. Connect QGroundControl to Pixhawk
2. Go to: **Analyze Tools** → **MAVLink Inspector**
3. Watch `RC_CHANNELS_OVERRIDE` messages

**What to Look For:**

```
RC_CHANNELS_OVERRIDE.chan1_raw: 1000-2000
RC_CHANNELS_OVERRIDE.chan2_raw: 1000-2000
... (channels 3-8)
```

Values should change when you move joystick!

---

## 🚨 Troubleshooting

### Problem: Joystick moves but PWM stays at 1500

**Causes:**

1. ❌ **Not Armed** - System won't send thruster commands
2. ❌ **Deadzone** - Movement too small (<3%)
3. ❌ **Calibration delay** - Wait 1.5s after startup

**Solution:**

```python
# Check armed state
if self.armed:
    pixhawk.send_rc_channels_override(channels)
```

---

### Problem: PWM changes but thrusters don't spin

**Causes:**

1. ❌ **Pixhawk not armed** - Check arm status LED
2. ❌ **Wrong flight mode** - Use MANUAL or STABILIZE
3. ❌ **ESC not calibrated** - Run ESC calibration
4. ❌ **No power** - Check battery voltage (>12V)
5. ❌ **Motor direction** - Check CW/ACW configuration

**Check List:**

- [ ] Battery connected and charged
- [ ] ESCs show green/blue LED
- [ ] Pixhawk armed (safety switch pressed)
- [ ] Flight mode = MANUAL
- [ ] PWM values visible in QGroundControl

---

### Problem: Network connection fails

**Causes:**

1. ❌ **Pi not powered on**
2. ❌ **Wrong network** - Check Ethernet cable
3. ❌ **MAVProxy not running**

**Solution:**

```bash
# SSH to Pi
ssh pi@raspberrypi.local

# Check MAVProxy
ps aux | grep mavproxy

# Start if needed
cd ~/mariner/pi_scripts
./start_pi_services.sh
```

---

## 📊 Verification Checklist

### Before Testing:

- [ ] Battery charged (>12V)
- [ ] Pixhawk powered and booted
- [ ] Raspberry Pi powered and connected
- [ ] MAVProxy running on Pi (port 7000)
- [ ] Network connection working
- [ ] Joystick connected to PC
- [ ] ROV secured or in water

### During Testing:

- [ ] Joystick detected in system
- [ ] PWM values changing (1000-2000)
- [ ] MAVLink messages being sent
- [ ] Pixhawk receiving messages
- [ ] System armed
- [ ] Flight mode = MANUAL

### Safety:

- [ ] Emergency stop button mapped (Start button)
- [ ] Neutral values on disconnect (1500μs)
- [ ] Able to disarm quickly
- [ ] ROV in water or secured to test stand

---

## 📚 Key Files Reference

| File                                    | Purpose                        | Key Functions                                                     |
| --------------------------------------- | ------------------------------ | ----------------------------------------------------------------- |
| `src/controllers/joystickController.py` | Read joystick & convert to PWM | `read_joystick()`, `compute_thruster_channels()`, `axis_to_pwm()` |
| `src/connections/mavlinkConnection.py`  | MAVLink communication          | `send_rc_channels_override()`, `arm()`, `disarm()`                |
| `src/ui/marinerApp.py`                  | Main application               | `control_loop()`, `toggle_arm()`                                  |
| `config.json`                           | Configuration                  | Connection string, update rate                                    |
| `test_thruster_dataflow.py`             | Complete test suite            | End-to-end testing                                                |
| `diagnose_thruster_flow.ps1`            | Quick diagnostic               | System check                                                      |

---

## 💡 Important Notes

1. **Always ARM before thrusters will work!**

   - Location: ARM button in GUI
   - Keyboard: Handled by arm toggle

2. **PWM 1500 = STOPPED**

   - This is neutral/center position
   - No movement at this value

3. **Direction depends on motor wiring**

   - CW (clockwise) thrusters: higher PWM = forward
   - ACW (counter-clockwise): lower PWM = forward
   - Check motor direction in QGroundControl

4. **Control loop runs at 10Hz**

   - Sends commands 10 times per second
   - Configurable in config.json

5. **Network is crucial**
   - Without Pi connection, no control
   - Auto-reconnect implemented
   - Check network status in GUI

---

## 🎯 Quick Test Command

```bash
# Complete system test (recommended)
python test_thruster_dataflow.py

# Just joystick test
python test_controller.py

# Launch full application
python launch_mariner.py
```

---

**✅ If everything is working:**

- Joystick moves → PWM changes → Network sends → Pixhawk receives → Motors spin

**❌ If something fails:**

- Use diagnostic script to find the broken link in the chain
- Check each stage independently
- Review troubleshooting section above

---

**Need more help?** Check:

- `TROUBLESHOOTING.md` - Common issues and fixes
- `QUICK_REFERENCE.md` - Controls and mappings
- `CONNECTION_DIAGRAM.md` - System architecture
