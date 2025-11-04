# PORT CONFIGURATION UPDATE ✅

## What Changed

Your Pixhawk is now detected on a different serial port with a different baud rate:

**Old Configuration:**

- Port: `/dev/ttyACM0` or `/dev/ttyACM1`
- Baud Rate: 115200

**New Configuration:**

- Port: `/dev/ttyAMA0` ✅
- Baud Rate: 57600 ✅

## Files Updated

### 1. **pi_scripts/mavproxy_service_wrapper.sh**

- Changed default baudrate: `115200` → `57600`
- Updated device detection: Checks `/dev/ttyAMA0` first
- Fallback order: ttyAMA0 → ttyACM0 → ttyACM1

### 2. **smart_start_mavproxy.sh**

- Updated device detection to check `/dev/ttyAMA0` first
- Changed baudrate in startup command: `115200` → `57600`

### 3. **pi_scripts/pi_mavproxy_server.py**

- Changed default master: `/dev/ttyACM0` → `/dev/ttyAMA0`
- Changed default baudrate: `115200` → `57600`

## Deployment Steps

Run this PowerShell script to deploy the changes to your Pi:

```powershell
.\update_mavproxy_port.ps1
```

This script will:

1. ✅ Upload updated scripts to Pi
2. ✅ Stop MAVProxy service
3. ✅ Update configuration files
4. ✅ Restart MAVProxy service
5. ✅ Check service status
6. ✅ Test TCP port 7000 connection

## Manual Deployment (Alternative)

If you prefer manual deployment:

```powershell
# 1. Upload files
scp pi_scripts/mavproxy_service_wrapper.sh pi@raspberrypi.local:/tmp/
scp smart_start_mavproxy.sh pi@raspberrypi.local:/tmp/
scp pi_scripts/pi_mavproxy_server.py pi@raspberrypi.local:/tmp/

# 2. SSH to Pi
ssh pi@raspberrypi.local

# 3. Update files (on Pi)
sudo cp /tmp/mavproxy_service_wrapper.sh /usr/local/bin/
sudo chmod +x /usr/local/bin/mavproxy_service_wrapper.sh
cp /tmp/smart_start_mavproxy.sh ~/
chmod +x ~/smart_start_mavproxy.sh
mkdir -p ~/mariner/pi_scripts
cp /tmp/pi_mavproxy_server.py ~/mariner/pi_scripts/
chmod +x ~/mariner/pi_scripts/pi_mavproxy_server.py

# 4. Restart service
sudo systemctl restart mavproxy.service

# 5. Check status
sudo systemctl status mavproxy.service
```

## Verification

### On Raspberry Pi:

```bash
# 1. Check if device exists
ls -la /dev/ttyAMA0

# Should show:
# crw-rw---- 1 root dialout 204, 64 Nov  4 XX:XX /dev/ttyAMA0

# 2. Check MAVProxy service
sudo systemctl status mavproxy.service

# Should show:
# Active: active (running)

# 3. Check logs
sudo journalctl -u mavproxy.service -n 50

# Should show:
# ✅ Found Pixhawk on /dev/ttyAMA0
# Starting MAVProxy...
# Device: /dev/ttyAMA0
# Baudrate: 57600

# 4. Test port
nc -zv localhost 7000

# Should show:
# Connection to localhost 7000 port [tcp/*] succeeded!
```

### On Windows PC:

```powershell
# Test connection to Pi
Test-NetConnection -ComputerName raspberrypi.local -Port 7000

# Should show:
# TcpTestSucceeded : True

# Launch application
python launch_mariner.py
```

## Expected Behavior

After deployment, you should see:

```
[CONNECT] Attempting to connect → tcp:raspberrypi.local:7000
[✅] Heartbeat received — Pixhawk Connected!
    System ID: X, Component ID: X
[PIXHAWK] ✅ Connected
```

## Troubleshooting

### "Port 7000 is closed"

Check MAVProxy logs:

```bash
ssh pi@raspberrypi.local "sudo journalctl -u mavproxy.service -f"
```

### "Device not found"

Verify the Pixhawk is connected:

```bash
ssh pi@raspberrypi.local "ls -la /dev/tty*"
```

Look for `/dev/ttyAMA0` or `/dev/ttyACM*`

### "Permission denied"

Add user to dialout group:

```bash
ssh pi@raspberrypi.local "sudo usermod -a -G dialout pi"
# Then logout and login again
```

### Still using old port

Force service reload:

```bash
ssh pi@raspberrypi.local "sudo systemctl daemon-reload && sudo systemctl restart mavproxy.service"
```

## Port Detection Priority

The scripts now check devices in this order:

1. **`/dev/ttyAMA0`** (Primary - your current device) ✅
2. `/dev/ttyACM0` (Fallback)
3. `/dev/ttyACM1` (Fallback)

This ensures compatibility with different Pixhawk connection types.

## About /dev/ttyAMA0

`/dev/ttyAMA0` is the **Raspberry Pi's hardware UART** (GPIO pins 14/15). This suggests:

- ✅ More stable connection than USB
- ✅ No USB device switching issues
- ✅ Direct serial communication
- ✅ Better for production use

The 57600 baud rate is a standard rate supported by most ArduPilot configurations.

## Next Steps

1. **Deploy the changes:**

   ```powershell
   .\update_mavproxy_port.ps1
   ```

2. **Test the connection:**

   ```powershell
   python launch_mariner.py
   ```

3. **Verify in UI:**

   - Look for: `🟢 Pixhawk: Connected (tcp:raspberrypi.local:7000)`

4. **Test manual controls:**
   - Click "ARM THRUSTERS"
   - Test the 4 directional buttons

## Success Indicators

✅ MAVProxy service running  
✅ Port 7000 open and accepting connections  
✅ Pixhawk showing green "Connected" status in UI  
✅ Able to ARM the system  
✅ Manual control buttons sending commands

---

**Status: Ready to Deploy** 🚀

Run: `.\update_mavproxy_port.ps1`
