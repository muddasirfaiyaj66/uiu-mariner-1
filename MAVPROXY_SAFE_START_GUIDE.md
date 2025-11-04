# MAVProxy Safe Startup - Quick Reference

## Problem Fixed

**Issue**: "Address already in use" error when starting MAVProxy server
**Cause**: Multiple instances of the server trying to use the same port
**Solution**: Automatic cleanup and safe restart

---

## ✅ How to Use (3 Methods)

### Method 1: From Windows (Recommended)

```powershell
.\start_pi_mavproxy_safe.ps1
```

**What it does:**

- Uploads the safe startup script to Pi
- Stops any existing MAVProxy processes
- Checks if Pixhawk is connected
- Starts MAVProxy server cleanly
- Shows status and connection info

---

### Method 2: Directly on Raspberry Pi

```bash
cd /home/pi/mariner/pi_scripts
./start_mavproxy_safe.sh
```

**What it does:**

- Kills all existing MAVProxy processes
- Frees up port 7000 if occupied
- Verifies Pixhawk connection
- Starts server with proper logging
- Shows startup status

---

### Method 3: Manual (Your Original Method, but Safe)

```bash
# Always stop existing instances first!
pkill -f pi_mavproxy_server.py

# Wait a moment
sleep 2

# Now start fresh
cd /home/pi/mariner/pi_scripts
nohup python3 pi_mavproxy_server.py \
  --master /dev/ttyACM1 \
  --baudrate 115200 \
  --port 7000 \
  > /tmp/mavproxy.log 2>&1 &
```

---

## 📋 Common Commands

### Check if MAVProxy is Running

```bash
ssh pi@192.168.0.182 "ps aux | grep pi_mavproxy_server"
```

### View Live Logs

```bash
ssh pi@192.168.0.182 "tail -f /tmp/mavproxy.log"
```

### Stop MAVProxy Server

```bash
ssh pi@192.168.0.182 "pkill -f pi_mavproxy_server.py"
```

### Check Port Status

```bash
ssh pi@192.168.0.182 "netstat -tuln | grep 7000"
```

### Find What's Using Port 7000

```bash
ssh pi@192.168.0.182 "sudo lsof -i :7000"
```

---

## 🔧 Troubleshooting

### "Pixhawk not found"

```bash
ssh pi@192.168.0.182 "ls -l /dev/ttyACM*"
```

- Check USB cable connection
- Try different USB port
- Restart Pixhawk

### "Port already in use" (Manual Fix)

```bash
# Find the process
ssh pi@192.168.0.182 "sudo lsof -i :7000"

# Kill it (replace PID with actual process ID)
ssh pi@192.168.0.182 "kill -9 <PID>"
```

### Server Crashes Immediately

```bash
# Check full log
ssh pi@192.168.0.182 "cat /tmp/mavproxy.log"

# Check Python errors
ssh pi@192.168.0.182 "python3 -c 'import pymavlink; print(pymavlink.__version__)'"
```

---

## 📁 Files Created

| File                         | Location                       | Purpose                     |
| ---------------------------- | ------------------------------ | --------------------------- |
| `start_mavproxy_safe.sh`     | `/home/pi/mariner/pi_scripts/` | Safe startup script on Pi   |
| `start_pi_mavproxy_safe.ps1` | `./` (Windows)                 | Remote startup from Windows |

---

## 🎯 Best Practices

1. **Always use the safe startup script** - It handles cleanup automatically
2. **Check logs after starting** - Verify connection is working
3. **One instance only** - The script ensures this automatically
4. **Monitor the connection** - Use `tail -f /tmp/mavproxy.log`

---

## ⚙️ Configuration

Edit these variables in the scripts if needed:

**Bash Script** (`start_mavproxy_safe.sh`):

```bash
MASTER_PORT="/dev/ttyACM1"    # Pixhawk USB port
BAUDRATE="115200"              # Communication speed
TCP_PORT="7000"                # Server listening port
```

**PowerShell Script** (`start_pi_mavproxy_safe.ps1`):

```powershell
-PiHost "192.168.0.182"       # Pi IP address
-MasterPort "/dev/ttyACM1"    # Pixhawk USB port
-Baudrate 115200               # Communication speed
-TcpPort 7000                  # Server listening port
```

---

## 📊 Success Indicators

When MAVProxy starts successfully, you should see:

```
✅ MAVProxy server started successfully!
PID: 1234
TCP Port: 7000
Log: /tmp/mavproxy.log
```

In the logs, you should see:

```
MAVLink message with ID 0
MAVLink message with ID 1
...
Heartbeat from system 1
```

---

## 🚀 Quick Start Workflow

1. **Start MAVProxy on Pi:**

   ```powershell
   .\start_pi_mavproxy_safe.ps1
   ```

2. **Verify it's running:**

   ```powershell
   ssh pi@192.168.0.182 "tail -20 /tmp/mavproxy.log"
   ```

3. **Connect from Windows:**

   - Update `mavlinkConnection.py` to use: `tcp:192.168.0.182:7000`
   - Run your application

4. **Monitor connection:**
   ```powershell
   ssh pi@192.168.0.182 "tail -f /tmp/mavproxy.log"
   ```

---

## Need Help?

- Check logs: `cat /tmp/mavproxy.log`
- Verify Pixhawk: `ls -l /dev/ttyACM*`
- Check network: `ping 192.168.0.182`
- Check port: `netstat -tuln | grep 7000`
