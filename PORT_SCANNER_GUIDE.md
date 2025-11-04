# Port Scanner & Auto-Detection Guide 🔌

## Overview

The Pixhawk Port Scanner automatically finds your Pixhawk connection by testing multiple serial ports and baud rates. This is especially useful when:

- Running on Raspberry Pi with multiple serial devices
- USB port names change (like /dev/ttyUSB0 → /dev/ttyUSB1)
- Unsure of correct baud rate
- Setting up new hardware

---

## Quick Usage

### Method 1: Standalone Scanner (Recommended)

```powershell
# Run the port finder utility
python find_pixhawk.py
```

This will:

1. ✅ Scan all common serial ports
2. ✅ Try standard baud rates (115200, 57600, 921600, 38400)
3. ✅ Wait for MAVLink heartbeat on each combination
4. ✅ Show you the working connection
5. ✅ Optionally update config.json automatically

### Method 2: Auto-Detection in App

Enable auto-detection in `config.json`:

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "mavlink_auto_detect": true
}
```

Now when the app starts:

- If main connection fails → automatically scans serial ports
- If Pixhawk found → uses that connection
- Shows detected port in status display

### Method 3: Python Script

```python
from src.connections.portScanner import quick_scan

# Quick scan
connection_string = quick_scan()
if connection_string:
    print(f"Found: {connection_string}")
else:
    print("No Pixhawk found")
```

---

## How It Works

### Ports Scanned

**Linux/Raspberry Pi:**

- `/dev/ttyAMA0` - Raspberry Pi GPIO UART
- `/dev/serial0` - Primary serial port
- `/dev/ttyUSB0` - USB serial adapter 0
- `/dev/ttyUSB1` - USB serial adapter 1
- `/dev/ttyACM0` - USB CDC device 0
- `/dev/ttyACM1` - USB CDC device 1

**Windows:**

- `COM3` - Common USB serial
- `COM4` - Common USB serial
- `COM5` - Common USB serial

### Baud Rates Tested

1. **115200** - Most common for Pixhawk/ArduSub
2. **57600** - Alternative standard rate
3. **921600** - High-speed option
4. **38400** - Lower speed fallback

### Detection Process

```
For each port:
  For each baud rate:
    1. Try to open connection
    2. Wait up to 10 seconds for heartbeat
    3. If heartbeat received → SUCCESS!
    4. If timeout → try next combination
```

---

## Configuration

### Custom Ports/Baud Rates

```python
from src.connections.portScanner import PixhawkPortScanner

# Custom configuration
scanner = PixhawkPortScanner(
    ports=['/dev/ttyUSB0', '/dev/ttyUSB1', 'COM5'],
    baud_rates=[115200, 57600],
    timeout=3,
    heartbeat_timeout=8
)

result = scanner.scan()
if result:
    port, baud = result
    print(f"Found on {port} @ {baud}")
```

### Integration with Your Code

```python
from src.connections.mavlinkConnection import PixhawkConnection

# Enable auto-detection
pixhawk = PixhawkConnection(
    link="udp:192.168.0.104:14550",  # Try this first
    auto_detect=True  # Scan serial if it fails
)

if pixhawk.connect():
    print(f"Connected via: {pixhawk.link}")
```

---

## Typical Scenarios

### Scenario 1: Raspberry Pi → Pixhawk (UART)

**Hardware:**

- Pi GPIO TX (pin 8) → Pixhawk TELEM2 RX
- Pi GPIO RX (pin 10) → Pixhawk TELEM2 TX
- Ground connected

**Expected Detection:**

```
[SCANNER] ✅ Heartbeat received on /dev/ttyAMA0 @ 115200 baud
Connection string: /dev/ttyAMA0:115200
```

**Config Update:**

```json
{
  "mavlink_connection": "/dev/ttyAMA0:115200"
}
```

### Scenario 2: Raspberry Pi → Pixhawk (USB)

**Hardware:**

- USB cable from Pi to Pixhawk USB port

**Expected Detection:**

```
[SCANNER] ✅ Heartbeat received on /dev/ttyACM0 @ 115200 baud
Connection string: /dev/ttyACM0:115200
```

**Config Update:**

```json
{
  "mavlink_connection": "/dev/ttyACM0:115200"
}
```

### Scenario 3: PC → Pixhawk (USB Cable)

**Hardware:**

- USB cable from Windows PC to Pixhawk

**Expected Detection:**

```
[SCANNER] ✅ Heartbeat received on COM4 @ 115200 baud
Connection string: COM4:115200
```

**Config Update:**

```json
{
  "mavlink_connection": "COM4:115200"
}
```

### Scenario 4: Network Connection (No Scanning)

**Hardware:**

- WiFi or Ethernet connection
- Pixhawk on companion computer

**Manual Config:**

```json
{
  "mavlink_connection": "udp:192.168.0.104:14550",
  "mavlink_auto_detect": false
}
```

---

## Troubleshooting

### No Device Found

**1. Check Physical Connection**

```bash
# Linux: List all serial devices
ls -l /dev/tty*

# Windows: Device Manager
# Look under "Ports (COM & LPT)"
```

**2. Check Permissions (Linux/Pi)**

```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Reboot required for group change
sudo reboot

# Or temporarily give permissions
sudo chmod 666 /dev/ttyUSB0
```

**3. Verify Pixhawk is Running**

- Power LED should be solid (not blinking in bootloader)
- ArduSub firmware loaded
- Try connecting with QGroundControl first

**4. Test Manually**

```bash
# Linux: Screen
screen /dev/ttyUSB0 115200
# Should see MAVLink binary data

# Windows: Use PuTTY
# Set Serial, COM4, 115200, 8N1
```

**5. Check USB Cable**

- Some cables are charge-only (no data)
- Try a different cable
- Test cable with another device

### Scanner Hangs

**Issue:** Scanner gets stuck waiting for heartbeat

**Solutions:**

```python
# Reduce timeouts
scanner = PixhawkPortScanner(
    timeout=3,           # Connection timeout
    heartbeat_timeout=5  # Heartbeat wait time
)
```

### Wrong Port Detected

**Issue:** Scanner finds wrong device (GPS, radio, etc.)

**Solution:** Specify exact ports to scan

```python
scanner = PixhawkPortScanner(
    ports=['/dev/ttyUSB0']  # Only scan this one
)
```

---

## Advanced Usage

### Scan Multiple Times

```python
from src.connections.portScanner import PixhawkPortScanner

scanner = PixhawkPortScanner()

# Try up to 3 times with 2 second delay
result = scanner.scan_with_retry(
    max_attempts=3,
    delay=2
)
```

### Custom Port List

```python
# Scan only specific devices
custom_ports = [
    '/dev/ttyUSB0',
    '/dev/ttyUSB1',
    '/dev/serial0'
]

scanner = PixhawkPortScanner(ports=custom_ports)
result = scanner.scan()
```

### High-Speed Connection

```python
# Try high-speed baud rates first
fast_bauds = [921600, 500000, 115200]

scanner = PixhawkPortScanner(baud_rates=fast_bauds)
result = scanner.scan()
```

---

## Connection String Formats

### Serial Port

```
Format: PORT:BAUDRATE

Examples:
  /dev/ttyUSB0:115200    (Linux USB)
  /dev/ttyAMA0:57600     (Pi GPIO)
  COM3:115200            (Windows)
  /dev/serial0:115200    (Pi primary)
```

### Network

```
Format: PROTOCOL:HOST:PORT

Examples:
  udp:192.168.0.104:14550    (UDP - most common)
  tcp:10.42.0.185:5760       (TCP)
  udpin:0.0.0.0:14550        (UDP input)
```

---

## Integration Examples

### Example 1: Main App with Auto-Detect

```python
from src.connections.mavlinkConnection import PixhawkConnection

# Will try UDP first, then scan serial if fails
pixhawk = PixhawkConnection(
    link="udp:192.168.0.104:14550",
    auto_detect=True
)

if pixhawk.connect():
    print(f"✅ Connected: {pixhawk.link}")
else:
    print("❌ Failed to connect")
```

### Example 2: Pre-Scan Before Connecting

```python
from src.connections.portScanner import quick_scan
from src.connections.mavlinkConnection import PixhawkConnection

# Scan first
connection = quick_scan()

if connection:
    # Use discovered connection
    pixhawk = PixhawkConnection(link=connection)
    pixhawk.connect()
else:
    # Fall back to default
    pixhawk = PixhawkConnection(link="udp:192.168.0.104:14550")
    pixhawk.connect()
```

### Example 3: Save Discovery for Later

```python
import json
from src.connections.portScanner import quick_scan

# Scan and save
connection = quick_scan()

if connection:
    config = {
        "mavlink_connection": connection,
        "discovered_at": time.time()
    }

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)
```

---

## Performance Tips

### Speed Up Scanning

1. **Reduce port list** - Only scan likely ports
2. **Try common baud first** - 115200 is most common
3. **Lower timeouts** - If you know device responds quickly
4. **Skip if network works** - Only scan when UDP/TCP fails

### Example: Fast Scan

```python
scanner = PixhawkPortScanner(
    ports=['/dev/ttyUSB0', '/dev/ttyACM0'],  # Only 2 ports
    baud_rates=[115200],                      # Only 1 baud rate
    timeout=2,                                # Quick timeout
    heartbeat_timeout=5                       # Quick heartbeat
)

result = scanner.scan()  # Much faster!
```

---

## Safety Notes

⚠️ **Auto-detection on Production Systems:**

- May connect to wrong device temporarily
- Can cause brief delays on startup
- Not recommended for time-critical applications

✅ **Best Practice:**

1. Use scanner to **discover** connection once
2. **Save** discovered connection to config
3. **Disable** auto-detect for normal operations
4. Only **re-enable** when hardware changes

---

## File Locations

```
mariner-software-1.0/
├── find_pixhawk.py                        ← Standalone scanner utility
├── src/
│   └── connections/
│       ├── portScanner.py                 ← Scanner module
│       └── mavlinkConnection.py           ← Uses scanner
└── config.json                            ← Stores discovered connection
```

---

## Summary

✅ **Use `find_pixhawk.py` for initial setup** - Easy, user-friendly  
✅ **Enable auto-detect during development** - Handles port changes  
✅ **Disable auto-detect in production** - Faster, more predictable  
✅ **Manual config for network connections** - No scanning needed

**Your code was the inspiration for this feature - thanks for sharing! 🎉**

---

_Auto-Detection Guide v1.0_  
_Part of UIU MARINER ROV Control System_
