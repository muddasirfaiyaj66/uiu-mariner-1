# 🚀 AUTO-CONNECT GUIDE - Simple & Automatic!

## What Changed?

✅ **Everything is now AUTOMATIC!**

- No need to manually find Pi IP address
- No need to manually start MAVProxy
- Just run your software and it works!

---

## 🎯 Quick Start (Super Simple!)

### Option 1: From Your Python Application (RECOMMENDED)

**Just change ONE line in your code:**

```python
# OLD WAY (manual IP):
# pixhawk = PixhawkConnection(link="tcp:192.168.0.182:7000")

# NEW WAY (automatic):
pixhawk = PixhawkConnection(link="auto")
```

**That's it!** The system will automatically:

1. 🔍 Find your Raspberry Pi on the network
2. 🚀 Start MAVProxy if it's not running
3. 🔌 Connect to Pixhawk
4. ✅ Ready to use!

---

### Option 2: Test Auto-Connect

Run this to test the auto-connection:

```powershell
python auto_mavlink_connect.py
```

You'll see:

```
==================================================
🔌 Auto-Connecting to Pixhawk via Pi
==================================================
🔍 Searching for Raspberry Pi on network...
✅ Found Pi at: 192.168.0.182

🔐 Verifying SSH connection to 192.168.0.182...
✅ SSH connection verified

🔍 Checking MAVProxy status...
✅ MAVProxy already running

🔌 Checking port 7000...
✅ Port is open and ready

==================================================
✅ READY TO CONNECT
==================================================
Connection String: tcp:192.168.0.182:7000
==================================================
```

---

## 📝 Example Usage in Your Code

### Simple Example

```python
from src.connections.mavlinkConnection import PixhawkConnection

# Auto-connect (handles everything)
pixhawk = PixhawkConnection(link="auto")
pixhawk.connect()

# Now use it normally
pixhawk.arm()
pixhawk.set_mode("STABILIZE")
# ... your code ...
```

### With Error Handling

```python
from src.connections.mavlinkConnection import PixhawkConnection
import sys

def main():
    print("Starting Ground Station Software...")

    # Auto-connect
    pixhawk = PixhawkConnection(link="auto")

    if not pixhawk.connect():
        print("Failed to connect to Pixhawk")
        print("Please check:")
        print("  1. Raspberry Pi is powered on")
        print("  2. Ethernet cable is connected")
        print("  3. Pixhawk is connected to Pi via USB")
        sys.exit(1)

    print("Connected successfully!")

    # Your ground station code here
    # ...

if __name__ == "__main__":
    main()
```

---

## 🔧 How It Works (Behind the Scenes)

When you use `link="auto"`, the system does this automatically:

```
1. 🔍 Scan network for Raspberry Pi
   ├─ Checks common IPs first (192.168.0.182, .100, .101, etc.)
   └─ Scans full subnet if needed

2. 🔐 Verify SSH connection to Pi
   └─ Confirms Pi is accessible

3. 🔍 Check if MAVProxy is running
   ├─ If YES → Use existing connection
   └─ If NO → Start MAVProxy automatically

4. 🔌 Verify port 7000 is open
   └─ Confirms MAVProxy is ready

5. ✅ Return connection string
   └─ e.g., "tcp:192.168.0.182:7000"

6. 🔌 Connect to Pixhawk
   └─ Your software is ready!
```

---

## 📋 What You Need

### One-Time Setup (Already Done!)

- ✅ `auto_mavlink_connect.py` - Auto-detection module
- ✅ `pi_scripts/auto_detect_pi.ps1` - IP detection script
- ✅ `start_pi_mavproxy_safe.ps1` - MAVProxy starter
- ✅ Updated `mavlinkConnection.py` - Supports "auto"

### Hardware Requirements

- ✅ Raspberry Pi connected via Ethernet
- ✅ Pixhawk connected to Pi via USB
- ✅ Both devices powered on
- ✅ Same network (through your ground station computer)

---

## 🎮 Your Workflow Now

### Before (Manual):

```
1. Find Pi IP address
2. SSH to Pi
3. Start MAVProxy manually
4. Check if it's running
5. Copy IP address
6. Update your code
7. Run your software
```

### Now (Automatic):

```
1. Run your software
   ↓
   DONE! ✅
```

---

## 🛠️ Troubleshooting

### "Could not detect Pi"

**Check:**

```powershell
# Is Pi responding to ping?
ping 192.168.0.182

# Can you SSH?
ssh pi@192.168.0.182

# Check Ethernet connection
Get-NetAdapter | Where-Object {$_.Status -eq "Up"}
```

### "MAVProxy failed to start"

**Check on Pi:**

```bash
# Is Pixhawk connected?
ls -l /dev/ttyACM*

# Check logs
cat /tmp/mavproxy.log
```

### "Connection timeout"

**Verify:**

```bash
# Is MAVProxy running?
ps aux | grep pi_mavproxy_server

# Is port open?
netstat -tuln | grep 7000
```

---

## ⚡ Advanced: Manual IP Override

If you know the IP and want to skip detection:

```python
# Specify IP but still auto-start MAVProxy
pixhawk = PixhawkConnection(link="tcp:192.168.0.182:7000")
pixhawk.connect()

# OR specify IP without auto-features
pixhawk = PixhawkConnection(
    link="tcp:192.168.0.182:7000",
    auto_detect=False
)
pixhawk.connect()
```

---

## 📊 Comparison

| Feature              | Before    | Now          |
| -------------------- | --------- | ------------ |
| **IP Detection**     | ❌ Manual | ✅ Automatic |
| **Start MAVProxy**   | ❌ Manual | ✅ Automatic |
| **Connection Check** | ❌ Manual | ✅ Automatic |
| **Lines of Code**    | Many      | ONE!         |
| **Startup Time**     | Minutes   | Seconds      |
| **Dynamic IP**       | ❌ Broken | ✅ Works     |

---

## 🎯 Bottom Line

### To use in your code:

```python
from src.connections.mavlinkConnection import PixhawkConnection

# Change this ONE line:
pixhawk = PixhawkConnection(link="auto")  # ← AUTO-MAGIC! ✨

# Everything else stays the same:
pixhawk.connect()
pixhawk.arm()
# ... your code ...
```

---

## 💡 Pro Tips

1. **Keep Pi powered on** before starting your software
2. **Wait ~5 seconds** after Pi boots for network to initialize
3. **Check logs** if having issues: `cat /tmp/mavproxy.log`
4. **Test auto-connect** first: `python auto_mavlink_connect.py`

---

## 🚀 Real-World Example

```python
#!/usr/bin/env python3
"""
Simple Ground Station - Auto-Connect Example
"""

from src.connections.mavlinkConnection import PixhawkConnection
import time

def main():
    print("=" * 50)
    print("Ground Station Starting...")
    print("=" * 50)

    # AUTO-CONNECT (handles everything!)
    pixhawk = PixhawkConnection(link="auto")

    if not pixhawk.connect():
        print("❌ Connection failed!")
        return

    print("✅ Connected!")
    print("=" * 50)

    # Set mode
    pixhawk.set_mode("STABILIZE")

    # Arm thrusters
    pixhawk.arm()

    # Control example
    print("Sending neutral commands...")
    for i in range(10):
        # Neutral position (1500 PWM on all channels)
        pixhawk.send_rc_channels_override([1500] * 8)
        time.sleep(0.1)

    # Disarm
    pixhawk.disarm()

    # Cleanup
    pixhawk.close()
    print("✅ Done!")

if __name__ == "__main__":
    main()
```

**Run it:**

```powershell
python my_ground_station.py
```

**Output:**

```
==================================================
Ground Station Starting...
==================================================
🔌 Auto-Connecting to Pixhawk via Pi
🔍 Searching for Raspberry Pi on network...
✅ Found Pi at: 192.168.0.182
✅ MAVProxy already running
✅ Port is open and ready
[CONNECT] Attempting to connect → tcp:192.168.0.182:7000
[✅] Heartbeat received — Pixhawk Connected!
✅ Connected!
==================================================
[MODE] → STABILIZE
[✅] Thrusters armed!
Sending neutral commands...
[⚠️] Thrusters disarmed
[DISCONNECT] Closing MAVLink connection
✅ Done!
```

---

## ✅ Summary

**What you need to remember:**

1. Use `link="auto"` in your code
2. That's it!

Everything else is handled automatically! 🎉

---

**Files to reference:**

- `auto_mavlink_connect.py` - Auto-connection module
- `AUTO_CONNECT_GUIDE.md` - This file
- `src/connections/mavlinkConnection.py` - Updated connection class
