# 🎯 CURRENT STATUS & NEXT STEPS

## ✅ What We Found

### Network Status:

- ✅ **Pi is ONLINE** at `192.168.0.102`
- ✅ **SSH is working** (port 22 open)
- ✅ **Your PC IP**: `192.168.0.104`
- ❌ **Pi services NOT running** (ports 5000, 5001, 7000 closed)

### The Problem:

**The Raspberry Pi is connected to the network, but the ROV services are not running.**

This is why you see:

```
[WinError 10061] No connection could be made because the target machine actively refused it
```

---

## 🚀 HOW TO FIX (Choose ONE method)

### Method 1: Automatic Start (Easiest) ⭐ RECOMMENDED

```powershell
.\start_pi_services_remote.ps1
```

This will:

1. SSH to the Pi automatically
2. Start all services with your PC IP
3. Return to Windows prompt

Then wait 10 seconds and verify:

```powershell
.\diagnose_pi_connection.ps1
```

---

### Method 2: Manual SSH (More Control)

#### Step 1: Connect to Pi

```powershell
ssh pi@raspberrypi.local
```

Password: `raspberry` (or your custom password)

#### Step 2: Start Services

```bash
cd ~/mariner/pi_scripts
./start_all_services.sh 192.168.0.104
```

#### Step 3: Verify Services Running

```bash
screen -ls
```

You should see:

```
There are screens on:
    12345.sensors    (Detached)
    12346.mavproxy   (Detached)
    12347.cam0       (Detached)
    12348.cam1       (Detached)
```

#### Step 4: Exit SSH

```bash
exit
```

#### Step 5: Test from Windows

```powershell
.\diagnose_pi_connection.ps1
```

All ports should show `[OK]`

---

### Method 3: First Time Setup (If services never installed)

If you've NEVER run setup on the Pi before:

```powershell
ssh pi@raspberrypi.local
```

Then on Pi:

```bash
cd ~/mariner/pi_scripts
./SETUP_AND_START.sh
```

Follow prompts:

1. Enter your PC IP: `192.168.0.104`
2. Choose option A or B for startup preference
3. Wait for installation to complete

---

## 🔍 About the Pixhawk Connection

**Important**: The Pixhawk connects to the **Raspberry Pi**, NOT directly to Windows.

```
Windows PC ←→ Network ←→ Raspberry Pi ←→ USB ←→ Pixhawk
```

### To Check Pixhawk on Pi:

```powershell
ssh pi@raspberrypi.local
```

Then:

```bash
# Check if Pixhawk is detected
ls /dev/ttyACM*

# Should show: /dev/ttyACM0
# If not found, run detection:
python3 ~/mariner/pi_scripts/detect_pixhawk.py
```

### If Pixhawk Not Found:

1. Check USB cable from Pixhawk to Pi
2. Check Pixhawk is powered (LED lights on)
3. Try different USB port on Pi
4. Reboot Pixhawk (disconnect/reconnect power)

---

## ✅ Complete Startup Procedure

### Every Time You Use the ROV:

1. **Power on Raspberry Pi** → Wait 30-60 seconds for boot

2. **Check Pi services** (from Windows):

   ```powershell
   .\diagnose_pi_connection.ps1
   ```

3. **If services not running**:

   ```powershell
   .\start_pi_services_remote.ps1
   ```

4. **Verify all OK**:

   ```powershell
   .\diagnose_pi_connection.ps1
   ```

   All ports should show `[OK]`

5. **Start Windows app**:

   ```powershell
   python launch_mariner.py
   ```

6. **Connect joystick** and start operations!

---

## 🔧 Troubleshooting

### "Connection Refused" Errors

→ Services not running on Pi
→ Run: `.\start_pi_services_remote.ps1`

### "Cannot reach Pi"

→ Pi not on network or powered off
→ Check power, network cable/WiFi

### Pixhawk Not Connected

→ Check USB from Pi to Pixhawk
→ SSH to Pi: `ls /dev/ttyACM*`

### Camera Streams Not Working

→ Check cameras connected to Pi
→ SSH to Pi: `./detect_cameras.sh`

### Services Keep Stopping

→ View logs via SSH: `screen -r mavproxy`
→ Check for error messages
→ Restart: `./stop_all_services.sh && ./start_all_services.sh 192.168.0.104`

---

## 📊 Port Reference

| Port | Service  | Protocol | Description                 |
| ---- | -------- | -------- | --------------------------- |
| 5000 | Sensors  | TCP      | BMP388 depth/pressure data  |
| 7000 | MAVProxy | TCP      | Pixhawk telemetry & control |
| 5000 | Camera 0 | UDP      | Front camera H.264 stream   |
| 5001 | Camera 1 | UDP      | Bottom camera H.264 stream  |

---

## 🎯 Next Steps - DO THIS NOW:

1. Run the automatic script:

   ```powershell
   .\start_pi_services_remote.ps1
   ```

2. Wait 10 seconds

3. Verify services:

   ```powershell
   .\diagnose_pi_connection.ps1
   ```

4. If all `[OK]`, start the app:

   ```powershell
   python launch_mariner.py
   ```

5. Once running, **SSH to Pi to check Pixhawk**:
   ```powershell
   ssh pi@raspberrypi.local
   ls /dev/ttyACM*
   exit
   ```

---

## 📝 Quick Command Reference

### Windows Commands:

```powershell
# Diagnose connection
.\diagnose_pi_connection.ps1

# Start Pi services remotely
.\start_pi_services_remote.ps1

# SSH to Pi
.\ssh_pi.ps1
# OR
ssh pi@raspberrypi.local

# Start main application
python launch_mariner.py
```

### Pi Commands (after SSH):

```bash
# Start all services
cd ~/mariner/pi_scripts
./start_all_services.sh 192.168.0.104

# Stop all services
./stop_all_services.sh

# View running services
screen -ls

# View specific log (Ctrl+A then D to exit)
screen -r sensors
screen -r mavproxy
screen -r cam0
screen -r cam1

# Check Pixhawk
ls /dev/ttyACM*
python3 detect_pixhawk.py

# Check cameras
./detect_cameras.sh
```

---

## ❓ Questions?

Read the detailed guides:

- `FIX_PI_NOT_CONNECTED.md` - Complete troubleshooting
- `pi_scripts/README_PI_SCRIPTS.md` - Pi script documentation
- `DEPLOYMENT_REAL_HARDWARE.md` - Hardware setup guide

---

**🎯 ACTION ITEM: Run `.\start_pi_services_remote.ps1` now!**
