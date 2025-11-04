# 🪟 Windows Installation & Setup Guide

## UIU MARINER ROV Control System

---

## ✅ Step-by-Step Installation (Windows 10/11)

### Step 1: Check Python Installation

Open PowerShell and check Python version:

```powershell
python --version
```

**Required**: Python 3.8 or higher (3.10+ recommended)

If not installed, download from: https://www.python.org/downloads/

**Important**: Check "Add Python to PATH" during installation!

---

### Step 2: Navigate to Project Folder

```powershell
cd "e:\UIU MARINER\mariner-software-1.0"
```

---

### Step 3: Create Virtual Environment

```powershell
python -m venv venv
```

This creates an isolated Python environment for the project.

---

### Step 4: Activate Virtual Environment

```powershell
.\venv\Scripts\Activate.ps1
```

**Troubleshooting**: If you get "execution policy" error:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Your prompt should now show `(venv)` at the beginning.

---

### Step 5: Install Dependencies

```powershell
pip install -r requirements.txt
```

This installs:

- `pymavlink` (MAVLink communication)
- `pygame` (Joystick input)
- `PyQt6` (GUI framework)
- `pyserial` (Serial communication)

**Wait time**: ~2-5 minutes depending on internet speed.

---

### Step 6: Configure Connection

Open `config.json` in Notepad and edit:

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "joystick_target": "xbox",
  "update_rate_hz": 10
}
```

**Common configurations:**

**Direct USB to Pixhawk:**

```json
"mavlink_connection": "serial:COM3:57600"
```

(Check COM port in Device Manager → Ports)

**Via Raspberry Pi:**

```json
"mavlink_connection": "udp:10.42.0.185:14550"
```

(Replace IP with your Pi's address)

---

### Step 7: Connect Joystick

1. Plug Xbox 360 controller into USB port
2. Windows should install drivers automatically
3. Press Xbox button to turn on controller
4. Verify in: `Control Panel` → `Devices and Printers` → `Game Controllers`

**Test joystick:**

- Right-click controller → Properties → Test
- Move sticks and verify axes respond

---

### Step 8: Test Without Hardware (Optional)

```powershell
python test_system.py
```

This runs offline tests to verify code integrity.

---

### Step 9: Launch Application

**Option A: Using launcher script** (Recommended)

```powershell
.\launch.ps1
```

**Option B: Direct Python command**

```powershell
python src\ui\rovControlApp.py
```

---

## 🎮 First-Time Usage Guide

### What You Should See

When the application launches:

1. **Window Title**: "UIU MARINER - ROV Control System"
2. **Connection Status Panel**:
   - "Pixhawk: Connected" (GREEN) ← Goal
   - "Joystick: Xbox 360 Controller" (GREEN) ← Goal
3. **Thruster Values**: All showing "1500" (neutral)

---

### If Pixhawk Shows "Disconnected" (RED)

**Troubleshooting checklist:**

1. **Check physical connection**

   - USB cable plugged in?
   - Pixhawk powered on? (LED blinking?)

2. **Check COM port** (for USB connection)

   ```powershell
   # List COM ports
   Get-WmiObject Win32_SerialPort | Select-Object Name, DeviceID
   ```

   Update `config.json` with correct COM port.

3. **Check IP address** (for network connection)

   - Can you ping the device?

   ```powershell
   ping 192.168.0.104
   ```

   - Is Raspberry Pi powered on?
   - Are PC and Pi on same network?

4. **Test with QGroundControl**

   - Download: https://qgroundcontrol.com/
   - Try connecting with same settings
   - If QGC works, your hardware is OK

5. **Check Windows Firewall**

   - Allow UDP port 14550
   - Or temporarily disable firewall for testing

6. **Try different connection method**
   - USB not working? Try network.
   - Network not working? Try USB.

---

### If Joystick Shows "Not Connected" (RED)

1. **Replug controller** into different USB port
2. **Press Xbox button** to wake controller
3. **Check Device Manager**:
   - Windows Key + X → Device Manager
   - Look under "Xbox Peripherals" or "Human Interface Devices"
   - Any yellow warning icons?
4. **Install Xbox 360 controller drivers**:
   - Usually automatic in Windows 10/11
   - Manual download: search "Xbox 360 controller driver Windows"

---

### Initial Operation Steps

Once both show GREEN:

1. **Select Flight Mode**

   - Click "MANUAL" button (recommended for testing)
   - Status should show "Mode: MANUAL"

2. **ARM Thrusters** ⚠️

   - Click "ARM THRUSTERS" button
   - Status changes to "Armed: YES" (GREEN, BOLD)
   - ⚠️ **CAUTION**: Thrusters can now spin!

3. **Test Joystick**

   - Gently move left stick forward
   - Watch thruster values change
   - Values should vary from ~1000-2000

4. **Emergency Stop Test** 🔴

   - Press Start button on controller
   - All thrusters should jump back to 1500
   - Status should show "EMERGENCY STOP ACTIVATED"

5. **When Done**
   - Click "DISARM THRUSTERS" (button turns back to green)
   - Or close window (auto-disarms on exit)

---

## 🔧 Advanced Configuration

### Change Update Rate

In `config.json`:

```json
"update_rate_hz": 20
```

- **10 Hz**: Default, smooth, low CPU
- **20 Hz**: More responsive, higher CPU
- **5 Hz**: Very low latency systems only

### Use Different Joystick

If you have multiple controllers:

```json
"joystick_target": null
```

This uses the first detected joystick (any brand).

Or specify partial name:

```json
"joystick_target": "Logitech"
```

### Disable Safety Checks (NOT RECOMMENDED)

```json
"enable_safety_checks": false
```

Only for experienced operators!

---

## 📊 Performance Monitoring

### Check CPU Usage

Open Task Manager (Ctrl+Shift+Esc):

- Look for `python.exe`
- Should be <5% CPU on modern PC
- High CPU? Close other apps

### Check Network Latency

```powershell
ping 192.168.0.104 -t
```

Should see <10ms for local network.

---

## 🐛 Common Error Messages

### "Import Error: No module named 'pygame'"

**Solution:**

```powershell
.\venv\Scripts\Activate.ps1
pip install pygame
```

### "Failed to connect to Pixhawk"

**Check:**

1. Pixhawk powered on?
2. Correct IP/COM port in config.json?
3. Windows Firewall blocking?

### "Connection timed out"

**Solutions:**

- Increase timeout in mavlinkConnection.py (line ~18)
- Check network cable
- Restart Pixhawk

### "No joystick detected"

**Solutions:**

- Replug USB
- Different USB port (try USB 2.0 vs 3.0)
- Update controller drivers

---

## 🔄 Daily Operation Routine

### Before Each Session

```powershell
# 1. Open PowerShell
# 2. Navigate to project
cd "e:\UIU MARINER\mariner-software-1.0"

# 3. Activate environment
.\venv\Scripts\Activate.ps1

# 4. Launch
python src\ui\rovControlApp.py
```

### OR use the launcher:

```powershell
.\launch.ps1
```

### After Each Session

- Click "DISARM THRUSTERS"
- Close application
- Power off ROV (disconnect battery)
- Disconnect joystick

---

## 📦 Updating the Software

If you modify code or pull updates:

```powershell
# Re-activate environment
.\venv\Scripts\Activate.ps1

# Re-install dependencies (if requirements.txt changed)
pip install -r requirements.txt --upgrade

# Run tests
python test_system.py

# Launch
python src\ui\rovControlApp.py
```

---

## 🆘 Emergency Procedures

### Software Crash Mid-Operation

1. **DON'T PANIC** - Pixhawk has built-in failsafe
2. Close any error windows
3. Relaunch application immediately
4. Check Pixhawk still armed (LED indicator)
5. If stuck armed, use QGroundControl to disarm

### Runaway Thrusters

1. Press **Start** button on joystick
2. Click **EMERGENCY STOP** in GUI
3. Close application
4. Disconnect ROV battery (physical kill)

### Loss of Connection

- Application stops sending commands automatically
- Pixhawk enters failsafe mode (configurable in ArduSub)
- Default: Disarm after 5 seconds
- Verify failsafe settings in QGroundControl before operations!

---

## 🎓 Learning Path

### Beginner (Week 1)

1. Install software
2. Test joystick without Pixhawk
3. Connect to Pixhawk in air (props off!)
4. Practice arm/disarm
5. Test emergency stop

### Intermediate (Week 2)

1. Full system test in water
2. Tune joystick sensitivity
3. Try different flight modes
4. Record test footage

### Advanced (Week 3+)

1. Modify thruster mappings
2. Add custom features
3. Integrate sensor data
4. Mission planning

---

## 📞 Getting Help

### Check Documentation

1. `README.md` - Full guide
2. `QUICK_REFERENCE.md` - Field guide
3. `SUMMARY.md` - Technical details
4. `ARCHITECTURE.txt` - System diagram

### Test System

```powershell
python test_system.py
```

### Enable Debug Logging

Add to top of `src/ui/rovControlApp.py`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## ✅ Installation Checklist

Before first dive, verify:

- [ ] Python 3.8+ installed
- [ ] Virtual environment created (`venv` folder exists)
- [ ] Dependencies installed (`pip list` shows pymavlink, pygame, PyQt6)
- [ ] Joystick detected (green in GUI)
- [ ] Pixhawk connected (green in GUI)
- [ ] config.json configured correctly
- [ ] Emergency stop tested (Start button works)
- [ ] Arm/Disarm tested (no errors)
- [ ] Thruster values change when moving joystick
- [ ] QGroundControl can connect (optional but recommended)
- [ ] ArduSub firmware v4.5.6+ (check in QGC)
- [ ] ESCs calibrated (check in QGC)
- [ ] Failsafe configured (check in QGC)
- [ ] Battery charged and checked
- [ ] Physical emergency stop accessible (battery disconnect)

---

## 🎉 Success!

If all checks pass, you're ready for operations!

**Remember:**

- Always test in air first (props off)
- Never arm without water (ESCs will overheat)
- Keep emergency stop accessible
- Have a spotter/safety person
- Follow local regulations

**Happy Diving! 🌊**

---

**UIU MARINER Team**  
**Last Updated: November 2025**
