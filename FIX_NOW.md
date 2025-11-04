# 🚨 IMMEDIATE FIX - Run These Commands on Pi

## Problem Identified

1. Pixhawk is on `/dev/ttyACM1` not `/dev/ttyACM0`
2. Serial port has "multiple access" error - something else is using it
3. MAVProxy TCP server keeps crashing (EOF on TCP socket)

---

## 🎯 Solution - Run on Raspberry Pi NOW

### Step 1: SSH to Pi (you're already in!)

You're already logged in. Good!

### Step 2: Kill all MAVProxy processes

```bash
sudo pkill -9 mavproxy
ps aux | grep mavproxy
```

### Step 3: Check which port Pixhawk is on

```bash
ls -la /dev/ttyACM*
```

You should see `/dev/ttyACM1` (based on your error)

### Step 4: Check if anything is using the port

```bash
sudo lsof | grep ttyACM
```

If you see any processes, kill them:

```bash
sudo pkill -9 <process_name>
```

### Step 5: Start MAVProxy on the CORRECT port

```bash
mavproxy.py --master=/dev/ttyACM1 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

**Leave this running!** Don't close it.

---

## 🧪 Test from Windows (in a NEW terminal)

Open a **new PowerShell window** on Windows and run:

```powershell
python test_thruster_dataflow.py
```

---

## 🔧 If MAVProxy Still Crashes

The `device reports readiness to read but returned no data` error suggests:

### Option A: USB cable issue

- Replug the USB cable between Pi and Pixhawk
- Try a different USB cable
- Try a different USB port on the Pi

### Option B: Pixhawk power issue

- Ensure Pixhawk is powered (LED should be on)
- Check battery connection
- Check power module

### Option C: Baudrate issue

Try different baudrates:

```bash
mavproxy.py --master=/dev/ttyACM1 --baudrate=57600 --out=tcpin:0.0.0.0:7000
```

Or:

```bash
mavproxy.py --master=/dev/ttyACM1 --baudrate=115200 --out=tcpin:0.0.0.0:7000
```

---

## 🎯 Alternative: Test WITHOUT MAVProxy

Skip the TCP network entirely and test directly:

```bash
python3 ~/mariner/pi_scripts/test_thruster_direct.py
```

This will:

- Auto-detect the correct serial port
- Connect directly to Pixhawk
- Test each thruster one by one
- Show you if the hardware works

---

## 📝 Quick Reference

### Current Status:

- ✅ Pixhawk detected on `/dev/ttyACM1`
- ❌ Serial port has connection errors
- ❌ MAVProxy crashes with "device disconnected" error

### Most Likely Cause:

**Something is repeatedly trying to read from the serial port and failing**

### Quick Fix:

1. Kill everything: `sudo pkill -9 mavproxy python python3`
2. Wait 5 seconds: `sleep 5`
3. Test direct: `python3 ~/mariner/pi_scripts/test_thruster_direct.py`

This will tell you definitively if the hardware works!

---

## ⚡ Do This RIGHT NOW on Pi:

```bash
# Kill everything
sudo pkill -9 mavproxy
sudo pkill -9 python3

# Wait
sleep 5

# Upload the fixed script (you need to do this from Windows first!)
# Then run the direct test
cd ~/mariner/pi_scripts
python3 test_thruster_direct.py
```

---

## 🔄 From Windows: Upload Fixed Script

In a **new PowerShell window** on Windows:

```powershell
scp pi_scripts\test_thruster_direct.py pi@raspberrypi.local:~/mariner/pi_scripts/
scp pi_scripts\fix_mavproxy_connection.sh pi@raspberrypi.local:~/mariner/pi_scripts/
```

Then on Pi:

```bash
chmod +x ~/mariner/pi_scripts/fix_mavproxy_connection.sh
~/mariner/pi_scripts/fix_mavproxy_connection.sh
```

This will automatically fix everything!
