# MAVProxy "Address Already in Use" - FIXED! ✅

## Problem Summary

**Issue**: `[Errno 98] Address already in use` when starting MAVProxy server
**Root Cause**: Multiple instances of `pi_mavproxy_server.py` running on port 7000
**Impact**: Unable to start MAVProxy server, blocking Pixhawk communication

---

## ✅ Solution Implemented

Created **safe startup scripts** that automatically:

1. ✅ Kill any existing MAVProxy processes
2. ✅ Free up port 7000 if occupied
3. ✅ Verify Pixhawk connection
4. ✅ Start server cleanly with proper logging
5. ✅ Show startup status

---

## 📁 Files Created

### 1. `pi_scripts/start_mavproxy_safe.sh` (on Raspberry Pi)

Bash script that runs on the Pi with comprehensive startup checks:

- Kills old processes
- Checks port availability
- Verifies Pixhawk at `/dev/ttyACM1`
- Starts server with nohup
- Provides detailed status output

### 2. `start_pi_mavproxy_safe.ps1` (Windows)

PowerShell script to run from Windows:

- Uploads the bash script to Pi
- Makes it executable
- Cleans up old processes
- Starts MAVProxy remotely
- Shows results

### 3. `MAVPROXY_SAFE_START_GUIDE.md`

Complete reference guide with:

- Usage instructions
- Common commands
- Troubleshooting steps
- Configuration options

---

## 🚀 How to Use

### Quick Start (Recommended)

```powershell
.\start_pi_mavproxy_safe.ps1
```

**That's it!** The script handles everything automatically.

### What You'll See

```
Starting MAVProxy Server on Raspberry Pi
Pi Address: pi@192.168.0.182

[1/4] Uploading safe startup script...
[OK] Script uploaded

[2/4] Making script executable...
[OK] Permissions set

[3/4] Stopping existing MAVProxy instances...
[OK] Cleanup complete

[4/4] Starting MAVProxy server...

================================
✅ MAVProxy server started successfully!
PID: 2259
TCP Port: 7000
Log: /tmp/mavproxy.log
================================
```

---

## 📋 Verification

### Check if Running

```powershell
ssh pi@192.168.0.182 "ps aux | grep pi_mavproxy_server"
```

### View Logs

```powershell
ssh pi@192.168.0.182 "tail -f /tmp/mavproxy.log"
```

### Check Port

```powershell
ssh pi@192.168.0.182 "netstat -tuln | grep 7000"
```

Expected output:

```
tcp        0      0 0.0.0.0:7000            0.0.0.0:*               LISTEN
```

---

## 🔧 Manual Method (If Needed)

If you prefer to do it manually:

```bash
# 1. Always stop existing instances first
pkill -f pi_mavproxy_server.py

# 2. Wait for cleanup
sleep 2

# 3. Start fresh
cd /home/pi/mariner/pi_scripts
nohup python3 pi_mavproxy_server.py \
  --master /dev/ttyACM1 \
  --baudrate 115200 \
  --port 7000 \
  > /tmp/mavproxy.log 2>&1 &
```

---

## 🎯 Key Benefits

| Before                             | After                    |
| ---------------------------------- | ------------------------ |
| ❌ "Address already in use" errors | ✅ Automatic cleanup     |
| ❌ Manual process killing          | ✅ One-command startup   |
| ❌ Port conflicts                  | ✅ Port validation       |
| ❌ No status feedback              | ✅ Clear status messages |
| ❌ Difficult troubleshooting       | ✅ Detailed logging      |

---

## 🔍 What the Script Does

### Startup Sequence

1. **Process Check**: Searches for any running `pi_mavproxy_server.py`
2. **Cleanup**: Kills old processes (graceful first, force if needed)
3. **Port Check**: Verifies port 7000 is free (kills occupying process if needed)
4. **Hardware Check**: Confirms Pixhawk is at `/dev/ttyACM1`
5. **Log Management**: Backs up old log, creates fresh one
6. **Start Server**: Launches with nohup for persistent operation
7. **Verification**: Checks if process started successfully

### Safety Features

- ✅ Prevents multiple instances
- ✅ Validates hardware before starting
- ✅ Handles zombie processes
- ✅ Preserves old logs
- ✅ Returns clear error messages
- ✅ Non-interactive (works in scripts)

---

## 🛠️ Troubleshooting

### Script Fails to Upload

**Symptom**: `[ERROR] Failed to upload script`
**Solution**:

```powershell
# Check SSH connection
ssh pi@192.168.0.182 "echo Connected"

# Check directory exists
ssh pi@192.168.0.182 "ls -ld /home/pi/mariner/pi_scripts"
```

### Pixhawk Not Found

**Symptom**: `❌ ERROR: Pixhawk not found at /dev/ttyACM1`
**Solution**:

```bash
# Check available devices
ssh pi@192.168.0.182 "ls -l /dev/ttyACM*"

# If it's at different port, edit the script or use parameter
```

### Port Still in Use

**Symptom**: Port 7000 occupied after cleanup
**Solution**:

```bash
# Find what's using it
ssh pi@192.168.0.182 "sudo lsof -i :7000"

# Force kill the process
ssh pi@192.168.0.182 "sudo kill -9 <PID>"
```

### Server Starts but Crashes

**Symptom**: Process starts then immediately exits
**Solution**:

```bash
# Check full log
ssh pi@192.168.0.182 "cat /tmp/mavproxy.log"

# Common issues:
# - Python dependencies missing
# - Pixhawk not responding
# - Serial port permissions
```

---

## 📊 Success Indicators

### In Terminal

```
✅ MAVProxy server started successfully!
PID: 2259
TCP Port: 7000
```

### In Logs (`/tmp/mavproxy.log`)

```
MAVLink message with ID 0
MAVLink message with ID 1
...
Heartbeat from system 1
SYSTEM 1 ARMED: False
```

### Process Running

```bash
$ ps aux | grep pi_mavproxy_server
pi    2259  0.5  1.2  45680  25344  ?  S  10:30  0:02  python3 pi_mavproxy_server.py
```

### Port Listening

```bash
$ netstat -tuln | grep 7000
tcp  0  0  0.0.0.0:7000  0.0.0.0:*  LISTEN
```

---

## 🔄 Stopping the Server

### From Windows

```powershell
ssh pi@192.168.0.182 "pkill -f pi_mavproxy_server.py"
```

### On Pi

```bash
pkill -f pi_mavproxy_server.py
```

### Verify Stopped

```bash
ps aux | grep pi_mavproxy_server  # Should show nothing
netstat -tuln | grep 7000          # Should be empty
```

---

## ⚙️ Configuration

### Change Pixhawk Port

Edit `start_mavproxy_safe.sh`:

```bash
MASTER_PORT="/dev/ttyACM0"  # Change to your port
```

### Change TCP Port

```bash
TCP_PORT="8000"  # Change to desired port
```

### Change Baudrate

```bash
BAUDRATE="57600"  # Common alternative
```

---

## 🎓 Understanding the Fix

### Why This Happened

- MAVProxy server was started multiple times
- Each instance tried to bind to port 7000
- Second instance failed with "Address already in use"
- Processes weren't properly cleaned up

### How Safe Start Works

```
┌─────────────────────────┐
│ Start Request           │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Check Existing Process  │
└──────────┬──────────────┘
           │ Found? Yes
           ▼
┌─────────────────────────┐
│ Kill Process            │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Check Port 7000         │
└──────────┬──────────────┘
           │ Occupied? Yes
           ▼
┌─────────────────────────┐
│ Free Port               │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ Verify Pixhawk          │
└──────────┬──────────────┘
           │ Found? Yes
           ▼
┌─────────────────────────┐
│ Start Server            │
└──────────┬──────────────┘
           │
           ▼
┌─────────────────────────┐
│ ✅ Running              │
└─────────────────────────┘
```

---

## 📞 Quick Reference Commands

| Task              | Command                                                    |
| ----------------- | ---------------------------------------------------------- |
| **Start Server**  | `.\start_pi_mavproxy_safe.ps1`                             |
| **Stop Server**   | `ssh pi@192.168.0.182 "pkill -f pi_mavproxy_server.py"`    |
| **Check Status**  | `ssh pi@192.168.0.182 "ps aux \| grep pi_mavproxy_server"` |
| **View Logs**     | `ssh pi@192.168.0.182 "tail -f /tmp/mavproxy.log"`         |
| **Check Port**    | `ssh pi@192.168.0.182 "netstat -tuln \| grep 7000"`        |
| **Check Pixhawk** | `ssh pi@192.168.0.182 "ls -l /dev/ttyACM*"`                |

---

## ✨ Best Practices

1. **Always use the safe startup script** - It handles all edge cases
2. **Check logs after starting** - Verify connection is working
3. **Monitor the first few minutes** - Watch for errors
4. **Don't manually start** - Unless debugging
5. **Keep one instance only** - Multiple instances cause conflicts

---

## 🎉 Result

**Before**:

- Manual process management
- Port conflicts
- Unreliable startup
- No status feedback

**Now**:

- ✅ One-command startup
- ✅ Automatic cleanup
- ✅ Reliable operation
- ✅ Clear status messages
- ✅ Comprehensive logging

---

## 📖 Related Documentation

- `MAVPROXY_SAFE_START_GUIDE.md` - Detailed usage guide
- `pi_scripts/start_mavproxy_safe.sh` - Bash implementation
- `start_pi_mavproxy_safe.ps1` - PowerShell wrapper

---

## 🎯 Next Steps

1. ✅ MAVProxy server is running (PID: 2259)
2. ✅ Port 7000 is listening
3. ⏭️ Update your application to connect: `tcp:192.168.0.182:7000`
4. ⏭️ Test MAVLink communication
5. ⏭️ Monitor logs for any issues

**Connection String for Your App**:

```python
connection_string = "tcp:192.168.0.182:7000"
```

---

**Status**: ✅ **FIXED AND OPERATIONAL**  
**MAVProxy Server**: Running (PID 2259)  
**Port**: 7000 (Listening)  
**Connection**: `tcp:192.168.0.182:7000`
