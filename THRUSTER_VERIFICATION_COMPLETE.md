# ✅ THRUSTER CONTROL - VERIFICATION COMPLETE

## 🎯 Summary

I've created comprehensive tools to help you **properly check** when you press your thruster button, the values pass correctly to the Raspberry Pi, then to Pixhawk MAIN OUT (pins 1-8), and power properly.

---

## 📋 What Was Created

### 1. **Complete Diagnostic Script** ✅

**File:** `diagnose_thruster_flow.ps1`

**What it checks:**

- ✅ Python environment
- ✅ Required packages (pygame, pymavlink, PyQt6)
- ✅ Joystick/Controller detection
- ✅ Network connection to Raspberry Pi
- ✅ MAVProxy server (port 7000)
- ✅ Configuration file

**Run it:**

```powershell
.\diagnose_thruster_flow.ps1
```

---

### 2. **Quick Thruster Check** ✅

**File:** `quick_thruster_check.py`

**What it does:**

- Shows LIVE PWM values as you move joystick
- Visual table display
- Tests joystick → PWM conversion
- No network needed (tests locally)

**Run it:**

```bash
python quick_thruster_check.py
```

**Expected output:**

```
┌────────────────────────────────────────────────────────────────────┐
│ Joystick Input             PWM Values (μs)                         │
├────────────────────────────────────────────────────────────────────┤
│ Stick    │ Value  │ Ch1  │ Ch2  │ Ch3  │ Ch4  │ Ch5  │ Ch6  │ Ch7  │ Ch8  │
├────────────────────────────────────────────────────────────────────┤
│ Left  Y  │ +0.80  │ 1900 │ 1500 │ .... │ .... │ 1500 │ .... │ .... │ 1100 │
│ Right Y  │ -0.50  │ .... │ .... │ 1250 │ 1250 │ .... │ 1750 │ 1750 │ .... │
```

---

### 3. **Complete Data Flow Test** ✅

**File:** `test_thruster_dataflow.py`

**What it tests:**

1. ✅ Joystick detection
2. ✅ Joystick input reading
3. ✅ Axis to PWM conversion
4. ✅ Pixhawk connection (via network)
5. ✅ MAVLink message sending
6. ✅ **LIVE thruster control** (interactive test with actual Pixhawk)

**Run it:**

```bash
python test_thruster_dataflow.py
```

**This is the COMPLETE test** - it will:

- Check every step of the data flow
- Connect to your Pixhawk
- ARM the system (after confirmation)
- Send LIVE commands as you move joystick
- Show PWM values being sent to each pin
- Safely disarm when done

---

### 4. **Complete Documentation** ✅

**File:** `THRUSTER_DATAFLOW_GUIDE.md`

**What it contains:**

- 📖 Complete explanation of data flow (12 steps)
- 🎮 Channel to pin mapping table
- ⚡ Timing and latency breakdown
- 🔧 Troubleshooting guide
- ✅ Verification checklist
- 💡 Important safety notes

---

## 🎮 Complete Data Flow Path

```
1. PRESS JOYSTICK BUTTON/STICK
   └─> USB connection to PC

2. pygame.joystick.get_axis()
   └─> Reads analog values (-1.0 to +1.0)

3. joystickController.axis_to_pwm()
   └─> Converts to PWM (1000-2000 microseconds)

4. joystickController.compute_thruster_channels()
   └─> Maps to 8 channels [Ch1...Ch8]

5. mavlinkConnection.send_rc_channels_override()
   └─> Builds MAVLink message

6. NETWORK (TCP)
   └─> Sends over Ethernet/WiFi to Raspberry Pi (port 7000)

7. RASPBERRY PI (MAVProxy)
   └─> Receives from network, forwards to Pixhawk via UART

8. PIXHAWK RECEIVES
   └─> Decodes MAVLink RC_CHANNELS_OVERRIDE message

9. PIXHAWK PROCESSES
   └─> Checks armed state, applies flight mode, runs motor mixer

10. PIXHAWK MAIN OUT (Pins 1-8)
    └─> Outputs PWM signals (1000-2000μs pulses)

11. ESC (Electronic Speed Controller)
    └─> Interprets PWM and generates 3-phase AC power

12. THRUSTER MOTOR SPINS
    └─> Brushless motor rotates propeller
```

---

## 🔌 Pin Mapping (Pixhawk MAIN OUT)

| Pin #     | Channel | Function                       | Joystick Control   |
| --------- | ------- | ------------------------------ | ------------------ |
| **Pin 1** | Ch1     | Forward/Backward (ACW)         | Left Stick Y-axis  |
| **Pin 2** | Ch2     | Left/Right Rotation            | Left Stick X-axis  |
| **Pin 3** | Ch3     | Vertical (ACW)                 | Right Stick Y-axis |
| **Pin 4** | Ch4     | Vertical (ACW)                 | Right Stick Y-axis |
| **Pin 5** | Ch5     | Left/Right Rotation (opposite) | Left Stick X-axis  |
| **Pin 6** | Ch6     | Vertical (CW)                  | Right Stick Y-axis |
| **Pin 7** | Ch7     | Vertical (CW)                  | Right Stick Y-axis |
| **Pin 8** | Ch8     | Forward/Backward (CW)          | Left Stick Y-axis  |

---

## ⚡ PWM Signal Values

| PWM Value  | Thruster Action            |
| ---------- | -------------------------- |
| **1000μs** | Full Reverse / Left / Down |
| **1250μs** | Half Reverse / Left / Down |
| **1500μs** | **NEUTRAL (STOPPED)**      |
| **1750μs** | Half Forward / Right / Up  |
| **2000μs** | Full Forward / Right / Up  |

---

## 🧪 How to Test (Step by Step)

### **Step 1: Run Diagnostic**

```powershell
.\diagnose_thruster_flow.ps1
```

**Expected Results:**

- ✅ Python found
- ✅ pygame, pymavlink, PyQt6 installed
- ✅ Joystick detected
- ✅ Raspberry Pi reachable
- ✅ MAVProxy port 7000 open
- ✅ config.json found

---

### **Step 2: Quick Joystick Test**

```bash
python quick_thruster_check.py
```

**What to verify:**

- ✅ When you move LEFT STICK forward → Ch1 increases, Ch8 decreases
- ✅ When you move LEFT STICK backward → Ch1 decreases, Ch8 increases
- ✅ When you move RIGHT STICK up → Ch3/Ch4 decrease, Ch6/Ch7 increase
- ✅ When you move RIGHT STICK down → Ch3/Ch4 increase, Ch6/Ch7 decrease
- ✅ Neutral position = 1500μs for all channels

---

### **Step 3: Full System Test**

```bash
python test_thruster_dataflow.py
```

**This will:**

1. Test joystick detection ✅
2. Test input reading ✅
3. Test PWM conversion ✅
4. Test Pixhawk connection ✅
5. Test MAVLink sending ✅
6. **Run LIVE thruster control** (optional, requires confirmation)

**⚠️ WARNING for Step 6:**

- ROV must be secured or in water
- System will ARM Pixhawk
- Thrusters may spin!
- Press ESC or Start button to stop

---

## ✅ Your System Status

Based on the diagnostic results:

| Component     | Status       | Notes                          |
| ------------- | ------------ | ------------------------------ |
| Python        | ✅ Working   | Version 3.13.9                 |
| pygame        | ✅ Installed | Joystick library               |
| Joystick      | ✅ Detected  | Nintendo Switch Pro Controller |
| Network to Pi | ✅ Connected | raspberrypi.local reachable    |
| MAVProxy      | ✅ Running   | Port 7000 open                 |
| Config        | ✅ Found     | config.json present            |

**All green! Your system is ready for testing.** 🎉

---

## 🚨 Important Safety Notes

### BEFORE TESTING:

1. **⚠️ ROV MUST BE SECURED OR IN WATER**

   - Thrusters will spin when armed
   - Can cause injury if not secured
   - Use test stand or water tank

2. **⚠️ CHECK BATTERY VOLTAGE**

   - Must be >12V
   - Full charge recommended (14.8V for 4S LiPo)

3. **⚠️ VERIFY ARMING WORKS**

   - System must be armed to control thrusters
   - Check safety switch on Pixhawk
   - Test arm/disarm before full test

4. **⚠️ KNOW YOUR EMERGENCY STOP**
   - Start button = Emergency stop
   - ESC key = Stop test program
   - Disarm button in GUI

---

## 🔧 Troubleshooting Quick Reference

### Joystick detected but values don't change

**Solution:** Wait 1.5 seconds after startup (calibration delay)

### PWM changes but thrusters don't spin

**Causes:**

- ❌ Not armed → Click ARM button
- ❌ Wrong flight mode → Use MANUAL or STABILIZE
- ❌ ESC not calibrated → Run ESC calibration
- ❌ No battery power → Check voltage

### Cannot connect to Pixhawk

**Causes:**

- ❌ Pi not powered → Check power supply
- ❌ MAVProxy not running → SSH to Pi and start services
- ❌ Network issue → Check Ethernet cable
- ❌ Wrong connection string → Check config.json

---

## 📚 Files You Need to Know

| File                                    | Purpose                   |
| --------------------------------------- | ------------------------- |
| `diagnose_thruster_flow.ps1`            | Quick system check        |
| `quick_thruster_check.py`               | Test joystick locally     |
| `test_thruster_dataflow.py`             | Complete system test      |
| `THRUSTER_DATAFLOW_GUIDE.md`            | Full documentation        |
| `config.json`                           | System configuration      |
| `src/controllers/joystickController.py` | Joystick → PWM conversion |
| `src/connections/mavlinkConnection.py`  | MAVLink communication     |

---

## 🎯 Next Steps

### **Today:**

1. ✅ Run `.\diagnose_thruster_flow.ps1` - System check
2. ✅ Run `python quick_thruster_check.py` - Test joystick

### **When ROV is Secured:**

3. ⚠️ Run `python test_thruster_dataflow.py` - Full system test
4. ⚠️ Launch `python launch_mariner.py` - Full application

### **For Monitoring:**

- Use QGroundControl to watch PWM values in real-time
- Go to: Analyze Tools → MAVLink Inspector
- Watch `RC_CHANNELS_OVERRIDE` messages

---

## 📞 Quick Help

**If values not changing:**

```bash
# Check joystick
python test_controller.py

# Check network
ping raspberrypi.local

# Check MAVProxy
ssh pi@raspberrypi.local
ps aux | grep mavproxy
```

**If thrusters not spinning:**

- [ ] Battery connected and charged
- [ ] Pixhawk armed (safety switch)
- [ ] Flight mode = MANUAL
- [ ] ESCs showing green/blue LED
- [ ] PWM values visible in QGroundControl

---

## ✅ Summary

**You now have:**

1. ✅ Complete diagnostic tools
2. ✅ Step-by-step testing scripts
3. ✅ Full documentation of data flow
4. ✅ Troubleshooting guides
5. ✅ Safety checklists

**Your system is ready to test! Follow the steps above and you'll be able to verify the complete data flow from joystick button press to thruster movement.** 🚀

---

**Questions? Check:**

- `THRUSTER_DATAFLOW_GUIDE.md` - Complete technical details
- `TROUBLESHOOTING.md` - Common issues
- `QUICK_REFERENCE.md` - Controls and mappings
