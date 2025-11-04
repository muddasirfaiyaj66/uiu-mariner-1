# 🎯 ONE-LINE FIX - Do This Now!

## On Raspberry Pi (Required First!):

```bash
ssh pi@raspberrypi.local "cd /home/pi/mariner && ./START_NOW.sh 192.168.0.100"
```

_Replace `192.168.0.100` with your Windows PC's IP address_

---

## On Windows (After Pi is running):

```powershell
python launch_mariner.py
```

---

## ✅ That's It!

If you see:

```
[✅] Heartbeat received — Pixhawk Connected!
[CAMERAS] ✅ Dual camera feeds started
```

**You're connected!** 🎉

---

## 🆘 If It Still Doesn't Work:

### 1. Find Your Windows IP:

```powershell
ipconfig
# Look for: IPv4 Address. . . . . . . . . . . : 192.168.X.X
```

### 2. Test Pi Connection:

```powershell
ping raspberrypi.local
```

### 3. SSH into Pi and check services:

```bash
ssh pi@raspberrypi.local
ps aux | grep -E "mavproxy|libcamera|sensor"
```

Should show:

- ✅ `mavproxy` running
- ✅ `libcamera-vid` running (1 or 2 processes)
- ✅ `pi_sensor_server.py` running

---

## 📱 Quick Status Check (on Pi):

```bash
# Check all services in one command
ssh pi@raspberrypi.local "ps aux | grep -E 'mavproxy|libcamera|sensor' | grep -v grep"
```

---

## 🔧 Manual Start (if START_NOW.sh fails):

```bash
# SSH into Pi
ssh pi@raspberrypi.local

# Start MAVProxy manually
mavproxy.py --master=/dev/ttyACM0 --baudrate=115200 --out=tcpin:0.0.0.0:7000 &

# Start Camera (simple test)
cd /home/pi/mariner
./cam0.sh 192.168.0.100 &
```

---

## 💡 Why This Fixes It:

**Problem:** Your Windows PC tried to connect to `/dev/ttyACM0` directly (Linux device path)

**Solution:** Pi acts as bridge:

- Pi connects to Pixhawk via USB (`/dev/ttyACM0`)
- Pi runs MAVProxy server on port 7000
- Windows connects to Pi via network (`tcp:raspberrypi.local:7000`)

---

## ✅ Summary

1. **Run on Pi:** `./START_NOW.sh 192.168.0.100`
2. **Run on Windows:** `python launch_mariner.py`
3. **Done!** System should connect

Need detailed help? See `QUICK_FIX_GUIDE.md`
