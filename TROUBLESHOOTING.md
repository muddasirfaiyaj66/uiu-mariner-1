# 🔍 Troubleshooting Guide

## UIU MARINER ROV Control System

---

## Quick Diagnostic

Run this command first:

```powershell
python test_system.py
```

If all tests pass ✅ → Hardware issue  
If tests fail ❌ → Software issue

---

## Problem: Application Won't Start

### Error: "Python is not recognized"

**Cause**: Python not in PATH  
**Fix**:

1. Reinstall Python from python.org
2. Check "Add Python to PATH" during installation
3. Restart PowerShell

### Error: "No module named 'PyQt6'"

**Cause**: Dependencies not installed  
**Fix**:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Error: "Cannot activate venv"

**Cause**: PowerShell execution policy  
**Fix**:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Window opens then crashes immediately

**Cause**: Missing joystick or Pixhawk connection logic error  
**Debug**:

```powershell
python src\ui\rovControlApp.py 2>&1 | Tee-Object error.log
```

Check `error.log` for details.

---

## Problem: Pixhawk Won't Connect

### Status: "Pixhawk: Connection Failed" (RED)

**Step 1: Check Physical Connection**

- [ ] USB cable plugged into Pixhawk and PC?
- [ ] Pixhawk powered on? (LED blinking?)
- [ ] Try different USB cable
- [ ] Try different USB port on PC

**Step 2: Verify Connection String**

For **USB connection**:

1. Open Device Manager (Win+X → Device Manager)
2. Expand "Ports (COM & LPT)"
3. Find "USB Serial Device (COMx)" where x is the port number
4. Update config.json:
   ```json
   "mavlink_connection": "serial:COM3:57600"
   ```

For **Network connection**:

1. Check Raspberry Pi IP address:
   ```powershell
   ping 10.42.0.185
   ```
2. If no response:
   - Check network cable
   - Verify Pi powered on
   - Check PC and Pi on same network
3. Update config.json with correct IP:
   ```json
   "mavlink_connection": "udp:10.42.0.185:14550"
   ```

**Step 3: Test with QGroundControl**

1. Download QGroundControl: https://qgroundcontrol.com/
2. Open QGC
3. Go to: Application Settings → Comm Links
4. Add new link with same settings as config.json
5. Try to connect

**If QGC works**: Your hardware is fine, check software config  
**If QGC fails**: Hardware problem (cable, port, or Pixhawk)

**Step 4: Check Windows Firewall**

```powershell
# Allow UDP port 14550
New-NetFirewallRule -DisplayName "MAVLink UDP" -Direction Inbound -Protocol UDP -LocalPort 14550 -Action Allow
```

**Step 5: Verify ArduSub Running**

- Pixhawk LED should be solid or blinking (not red)
- In QGC: Check firmware version (should be ArduSub 4.5.6+)
- If firmware missing, flash ArduSub via QGC

---

## Problem: Joystick Not Detected

### Status: "Joystick: Not Connected" (RED)

**Step 1: Physical Check**

- [ ] Controller plugged into USB port?
- [ ] Xbox button pressed (controller powered on)?
- [ ] LED on controller lit?
- [ ] Try different USB port

**Step 2: Windows Recognition**

1. Open Device Manager
2. Look for:
   - "Xbox Peripherals" → "Xbox 360 Controller for Windows"
   - OR "Human Interface Devices" → "USB Input Device"
3. Any yellow warning icons?
   - **Yes**: Right-click → Update Driver
   - **No**: Controller recognized

**Step 3: Test in Windows**

1. Win+R → type `joy.cpl` → Enter
2. Properties → Test tab
3. Move sticks - axes should respond
4. Press buttons - lights should flash

**Step 4: Check pygame**

```powershell
python -c "import pygame; pygame.init(); pygame.joystick.init(); print(f'Joysticks: {pygame.joystick.get_count()}')"
```

Should output: `Joysticks: 1` (or higher)

**If 0**: Pygame can't see controller

- Reinstall pygame: `pip uninstall pygame && pip install pygame`
- Restart PC
- Try wired controller (not wireless)

**Step 5: Modify Joystick Filter**

In `config.json`:

```json
"joystick_target": null
```

This uses ANY detected joystick (not just Xbox).

---

## Problem: Thrusters Not Responding

### Joystick moves but thruster values stay at 1500

**Cause 1: Not Armed**

- Check status: "Armed: NO"
- **Fix**: Click "ARM THRUSTERS" button

**Cause 2: Joystick Not Ready**

- Wait 1.5 seconds after app starts (calibration delay)

**Cause 3: Deadzone**

- Small joystick movements ignored (±3%)
- **Fix**: Move stick further from center

**Cause 4: Joystick Mapping Wrong**

- Different controller than Xbox 360
- **Fix**: Edit `src/controllers/joystickController.py`
- Change axis indices in `read_joystick()` method

---

### Thruster values change but motors don't spin

**Check 1: ESC Calibration**

1. Open QGroundControl
2. Go to: Vehicle Setup → Motors
3. Run ESC calibration procedure
4. Test each motor individually

**Check 2: PWM Output Enabled**

1. In QGC: Parameters → SERVO_BLH_MASK
2. Should be set to enable channels 1-8
3. If 0, set to 255

**Check 3: Thrusters in Water**

- ESCs may not spin props in air (low resistance)
- **NEVER run ESCs dry for extended periods** (overheat)

**Check 4: Battery Voltage**

- Check battery voltage (should be >14V for 4S LiPo)
- Low voltage triggers failsafe

**Check 5: Pixhawk Pre-Arm Checks**

1. In QGC, check messages panel
2. Look for "Pre-arm: ..." errors
3. Common issues:
   - GPS lock required (disable if no GPS)
   - Compass calibration needed
   - Accelerometer calibration needed

---

## Problem: Erratic Movement / Thrusters Jittering

**Cause 1: Joystick Drift**

- Sticks not returning to center
- **Fix**: Increase deadzone in `joystickController.py`:
  ```python
  DEADZONE = 0.10  # Was 0.03
  ```

**Cause 2: Electromagnetic Interference**

- Thrusters/ESCs near Pixhawk causing noise
- **Fix**:
  - Increase distance between Pixhawk and ESCs
  - Add ferrite cores to motor wires
  - Shield/twist ESC wires

**Cause 3: Network Latency**

- Only for UDP/TCP connections
- **Check**:
  ```powershell
  ping 192.168.0.104 -n 100
  ```
  Latency should be <10ms, <1% packet loss
- **Fix**:
  - Use wired ethernet (not WiFi)
  - Reduce update rate in config.json (10 → 5 Hz)

---

## Problem: "Emergency Stop" Won't Stop Motors

**Immediate Action**:

1. Close application
2. Disconnect battery (physical kill switch)

**Root Cause Analysis**:

**Cause 1: Arming Stuck**

- Pixhawk still armed after emergency stop
- **Fix**: Add force disarm in `rovControlApp.py`:
  ```python
  def emergency_stop(self):
      # ... existing code ...
      self.pixhawk.disarm()
      time.sleep(0.1)
      self.pixhawk.disarm()  # Send twice for reliability
  ```

**Cause 2: MAVLink Commands Delayed**

- Network buffer full
- **Fix**: Flush connection before emergency stop

**Prevention**:

- Always have physical battery disconnect
- Test emergency stop before every dive
- Configure ArduSub failsafe timeout (5 seconds)

---

## Problem: Application Freezes / Hangs

**Symptom**: Window doesn't respond, GUI frozen

**Cause**: Blocking network operation on GUI thread

**Quick Fix**: Force close

```powershell
Get-Process python | Stop-Process -Force
```

**Permanent Fix**: Already implemented in code (non-blocking sockets)

**If persists**:

1. Update PyQt6: `pip install --upgrade PyQt6`
2. Reduce update rate in config.json (10 → 5 Hz)

---

## Problem: High CPU Usage

**Check Task Manager**:

- Python should be <5% CPU
- If >20%: Issue present

**Causes**:

1. **Update rate too high**

   - config.json: `"update_rate_hz": 5` (reduce from 10 or 20)

2. **Multiple Python processes**

   - Check: `Get-Process python`
   - Close old instances

3. **GUI rendering**
   - Close other applications
   - Update graphics drivers

---

## Problem: Connection Drops Randomly

**Symptom**: Works fine, then "Connection Failed" appears

**Cause 1: USB Power Saving**

1. Device Manager → USB Root Hub
2. Properties → Power Management
3. **Uncheck** "Allow computer to turn off this device"

**Cause 2: WiFi/Network Instability**

- Use wired ethernet
- Static IP for Pi (not DHCP)

**Cause 3: Pixhawk Watchdog**

- Pixhawk rebooting due to error
- Check QGC logs for errors

---

## Problem: Wrong Thruster Moves

**Example**: Push forward, but ROV goes sideways

**Cause**: Thruster channel mapping wrong

**Fix**: Edit `src/controllers/joystickController.py`

Find `compute_thruster_channels()` method:

```python
# Current mapping (for reference)
channels[0] = value         # Ch1: Forward (Left)
channels[1] = value         # Ch2: Yaw (Right Lateral)
channels[2] = value2        # Ch3: Vertical (Front)
channels[3] = value2        # Ch4: Vertical (Rear)
channels[4] = value2        # Ch5: Yaw (Left Lateral)
channels[5] = value         # Ch6: Vertical (Front)
channels[6] = value         # Ch7: Vertical (Rear)
channels[7] = reverse_value # Ch8: Forward (Right)
```

**Swap channels** to match your physical thruster layout.

**Test procedure**:

1. Arm in air (props off!)
2. Push left stick forward
3. Note which channel shows >1500 in GUI
4. If wrong, swap channel indices in code

---

## Error Messages Explained

### "Import 'X' could not be resolved"

- VS Code linting issue (not runtime error)
- Safe to ignore if code runs
- Fix: Restart VS Code, or add to Python path

### "Heartbeat timeout"

- Pixhawk not responding within 10 seconds
- Check connection cable
- Verify Pixhawk powered on

### "Target system not found"

- MAVLink connection established but Pixhawk not sending heartbeat
- Check ArduSub firmware loaded
- Verify baud rate (57600 for serial)

### "RC override not working"

- Pixhawk in wrong mode
- Switch to MANUAL mode
- Check SYSID_MYGCS parameter matches

---

## Debug Mode

Enable verbose logging:

Edit `src/ui/rovControlApp.py`, add at top:

```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

Output saved to `debug.log`:

```powershell
python src\ui\rovControlApp.py 2>&1 | Tee-Object debug.log
```

---

## Still Not Working?

### Collect System Info

Run this diagnostic script:

```powershell
# Save as diagnostic.ps1
"=== System Information ===" > diagnostic.txt
python --version >> diagnostic.txt
"" >> diagnostic.txt

"=== Python Packages ===" >> diagnostic.txt
pip list >> diagnostic.txt
"" >> diagnostic.txt

"=== COM Ports ===" >> diagnostic.txt
Get-WmiObject Win32_SerialPort | Select-Object Name, DeviceID >> diagnostic.txt
"" >> diagnostic.txt

"=== Network Interfaces ===" >> diagnostic.txt
ipconfig >> diagnostic.txt
"" >> diagnostic.txt

"=== Test Results ===" >> diagnostic.txt
python test_system.py >> diagnostic.txt
```

Then review `diagnostic.txt` for issues.

---

## Contact / Support

1. Check `README.md` for full documentation
2. Review `ARCHITECTURE.txt` for system design
3. Run `test_system.py` for automated checks
4. Enable debug logging for detailed traces

---

**Most Common Issues (90% of problems)**:

1. ❌ Virtual environment not activated → `.\venv\Scripts\Activate.ps1`
2. ❌ Wrong COM port → Check Device Manager
3. ❌ Firewall blocking UDP → Allow port 14550
4. ❌ Not armed → Click "ARM THRUSTERS"
5. ❌ ESCs not calibrated → Use QGroundControl

**Prevention is better than cure**:

- ✅ Test with QGroundControl first
- ✅ Calibrate ESCs before operations
- ✅ Configure failsafes
- ✅ Have physical kill switch
- ✅ Run pre-flight checklist

---

**Last Resort: Clean Reinstall**

```powershell
# Delete virtual environment
Remove-Item -Recurse -Force venv

# Recreate
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

# Test
python test_system.py

# Run
python src\ui\rovControlApp.py
```

---

**Good luck! 🍀**
