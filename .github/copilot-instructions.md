# UIU MARINER ROV - Copilot Instructions

## Project Overview

**UIU MARINER** is a **ground station control system** for an underwater ROV (Remotely Operated Vehicle). This is NOT embedded software - it runs on a Windows PC and communicates with a Raspberry Pi + Pixhawk system on the ROV over a network.

**Critical Architecture Pattern**: Two-computer system:

- **Ground Station (this codebase)**: Windows PC with Xbox controller, camera display, PyQt6 GUI
- **ROV**: Raspberry Pi + Pixhawk + 8 thrusters + cameras + sensors (underwater)

Communication: Ground Station ←→ Network (WiFi/Ethernet) ←→ Raspberry Pi ←→ Serial ←→ Pixhawk

## Core Technologies

- **PyQt6**: GUI framework (main application in `src/ui/marinerApp.py`)
- **pymavlink**: MAVLink protocol for Pixhawk communication over UDP/TCP
- **pygame**: Xbox 360/compatible gamepad input
- **OpenCV + GStreamer**: Camera video streaming (H.264 via UDP)
- **QThreads**: Camera, sensor, and control workers run asynchronously

## Essential File Structure

```
src/
├── ui/
│   ├── marinerApp.py         # Main application entry point (1438 lines)
│   ├── cameraWorker.py       # QThread for dual camera feeds + OpenCV detection
│   ├── sensorWorker.py       # QThread for depth/temp/pressure telemetry
│   └── rovControlApp.py      # Legacy simpler control (superseded by marinerApp)
├── connections/
│   ├── mavlinkConnection.py  # PixhawkConnection class - handles MAVLink over network
│   └── portScanner.py        # Auto-detect serial ports (for direct Pi connections)
├── controllers/
│   └── joystickController.py # Xbox controller → 8-channel thruster PWM conversion
config.json                    # ALL runtime configuration (network IPs, ports, pipelines)
launch_mariner.py              # Application launcher with dependency checks
simple_auto_connect.py         # Auto-detect Raspberry Pi IP and start MAVProxy
```

## Critical Configuration Pattern

**ALL configuration is in `config.json`** - never hardcode IPs, ports, or pipelines:

```json
{
  "mavlink_connection": "tcp:raspberrypi.local:7000", // Network to Pi, NOT serial
  "joystick_target": null, // Auto-detect Xbox controller
  "camera": {
    "pipeline0": "udpsrc port=5000 ! ...", // GStreamer pipeline strings
    "pipeline1": "udpsrc port=5001 ! ..."
  },
  "sensors": {
    "host": "raspberrypi.local",
    "port": 5002,
    "mock_mode": false, // Enable for testing without hardware
    "auto_connect": true,
    "auto_fallback": true // Falls back to mock data on connection failure
  }
}
```

**Testing without hardware**: Set `sensors.mock_mode: true` and use `videotestsrc` in camera pipelines.

## MAVLink Communication Pattern

**Key Insight**: Ground station never connects to Pixhawk directly via serial. Flow is:

1. Ground Station → `mavlinkConnection.py` → Network (UDP/TCP)
2. Raspberry Pi runs `pi_mavproxy_server.py` (port 7000) to forward MAVLink
3. Raspberry Pi → Serial (`/dev/ttyACM0` or `/dev/ttyUSB0`) → Pixhawk
4. Pixhawk → PWM signals → 8 ESCs/Thrusters

**Auto-connection**: `simple_auto_connect.py` scans network for Pi, starts MAVProxy if needed, returns connection string. Used by `mavlinkConnection.py` when `link="auto"`.

**RC_CHANNELS_OVERRIDE pattern**: Direct thruster control via 8-channel PWM (1000-2000):

- 1500 = neutral
- 1000-1499 = reverse/left/down
- 1501-2000 = forward/right/up

```python
# Example from joystickController.py
channels = [1500, 1500, 1500, 1500, 1500, 1500, 1500, 1500]  # All neutral
pixhawk.send_rc_channels_override(channels)
```

## Thruster Channel Mapping (ArduSub Standard)

**8 thrusters** controlled via channels 1-8 (defined in `config.json`):

| Channel | Function         | Thruster Location |
| ------- | ---------------- | ----------------- |
| 1       | Forward/Backward | Left Front        |
| 2       | Yaw Left         | Left Lateral      |
| 3       | Vertical         | Front Left        |
| 4       | Vertical         | Front Right       |
| 5       | Yaw Right        | Right Lateral     |
| 6       | Vertical         | Rear Left         |
| 7       | Vertical         | Rear Right        |
| 8       | Forward/Backward | Right Front       |

See `joystickController.compute_thruster_channels()` for mixing logic.

## Threading Model

**Critical**: GUI (PyQt6) runs in main thread. Workers use QThreads:

- **CameraWorker** (x2): Continuously reads GStreamer pipeline, decodes H.264, applies OpenCV detection, emits QPixmap signals
- **SensorTelemetryWorker**: TCP socket to Pi (port 5002), parses JSON sensor data, auto-fallback to mock
- **Control Loop**: `QTimer` in `marinerApp.py` (4 Hz) reads joystick → sends RC_CHANNELS_OVERRIDE

**Signals used**: `frame_ready`, `fps_update`, `data_received`, `connection_status`, `error_occurred`

**Never block the main thread** - all I/O in workers. Connection checks are non-blocking with rate limiting.

## Network Auto-Detection Pattern

1. **Ground Station finds Pi**: mDNS (`raspberrypi.local`) or `simple_auto_connect.py` scans common IPs
2. **Pi finds Ground Station**: `get_ground_station_ip.py` on Pi checks SSH client IP, gateway, or ARP table
3. **Dynamic configuration**: Both sides auto-detect and update streaming targets

See `simple_auto_connect.py` and `pi_scripts/get_ground_station_ip.py`.

## Testing Workflow

**Without hardware** (common during development):

1. Set `config.json` → `sensors.mock_mode: true`
2. Change camera pipelines to `"videotestsrc ! videoconvert ! appsink"`
3. Run `python launch_mariner.py` - GUI runs with test patterns and simulated sensors

**With joystick only**:

```bash
python test_joystick.py  # Verify Xbox controller input
```

**With network to ROV**:

```bash
python test_mavlink_connection.py  # Test MAVLink connectivity
python test_system.py               # Full integration test
```

**All test files** are in project root (`test_*.py`) - simple standalone scripts, not pytest.

## Deployment to Raspberry Pi

**Ground station scripts** (PowerShell on Windows):

- `setup.ps1` - Create venv and install dependencies
- `launch_mariner.py` - Start application with checks
- `simple_auto_connect.py` - Auto-detect Pi and setup MAVProxy

**Pi-side scripts** (`pi_scripts/` directory):

- `pi_mavproxy_server.py` - MAVLink TCP server (port 7000)
- `pi_camera_server.py` - Stream H.264 to Ground Station
- `pi_sensor_server.py` - BMP388 sensor TCP server (port 5002)
- `start_all_services.sh` - Launch everything on Pi

**Remote deployment** (from Ground Station):

```powershell
.\update_pi_files.ps1  # SCP files to Pi
ssh pi@raspberrypi.local "cd ~/mariner/pi_scripts && ./start_all_services.sh"
```

## Common Gotchas

1. **"Pixhawk not connected" on Ground Station is normal** if Pi isn't running MAVProxy - check Pi, not local serial ports
2. **TCP connections disconnect immediately**: Always use `autoreconnect=True` in `mavutil.mavlink_connection()` for TCP/UDP links - prevents connect-disconnect loops
3. **Camera feeds require GStreamer** installed on Windows (runtime + dev packages) - OpenCV must be built with GStreamer support
4. **Joystick connects to PC, not ROV** - common confusion. Xbox controller via USB/Bluetooth to Ground Station
5. **Port conflicts**: Camera (5000, 5001), Sensors (5002), MAVLink (14550 or 7000) - Pi reserves 5000/5001 for cameras
6. **Auto-reconnection**: `mavlinkConnection.py` has built-in reconnect logic - don't add manual retry loops in UI
7. **Rate limiting**: RC_CHANNELS_OVERRIDE limited to 20 Hz in `send_rc_channels_override()` - avoid faster sending
8. **Don't close TCP connections during reconnect**: Let pymavlink's `autoreconnect` handle it - closing creates new connections unnecessarily

## Key Conventions

- **Error handling**: Print to console with emoji prefixes (`[✅]`, `[❌]`, `[⚠️]`) for easy scanning
- **Connection strings**: Format `"protocol:host:port"` - e.g., `"tcp:192.168.0.104:7000"` or `"udp:raspberrypi.local:14550"`
- **PWM values**: Always clamp to 1000-2000 range before sending
- **Deadzone**: Joystick axes have 3% deadzone (`JoystickController.DEADZONE = 0.03`)
- **Virtual environment**: Always recommend `setup.ps1` for new users - avoids system Python pollution

## Documentation Files

Extensive markdown docs exist but many are outdated/duplicate. **Authoritative sources**:

- `README.md` - Current overview
- `ARCHITECTURE.md` - System architecture (explains two-computer pattern)
- `QUICKSTART.md` - 5-minute getting started
- `config.json` - All runtime settings

**Ignore**: Files like `DO_THIS_NOW.md`, `FIX_NOW.md`, etc. are historical troubleshooting notes.

## When Making Changes

- **Network settings**: Update `config.json`, never hardcode
- **Thruster logic**: Modify `joystickController.compute_thruster_channels()`
- **UI layout**: Main window defined in `marinerApp.py` (code) and potentially `.ui` files (Qt Designer)
- **Camera detection**: Edit `cameraWorker._init_detector()` - currently uses Haar Cascades
- **Connection logic**: `mavlinkConnection.py` handles all Pixhawk communication
- **Testing**: Create standalone `test_*.py` in root - keep them simple, no frameworks

## Build/Run Commands

```powershell
# Initial setup
.\setup.ps1                           # Create venv + install deps

# Running
python launch_mariner.py              # Recommended launcher
python src/ui/marinerApp.py           # Direct run

# Testing
python test_joystick.py               # Test controller input
python test_mavlink_connection.py     # Test network to ROV
python test_system.py                 # Full system test
```

No build step - pure Python. Virtual environment strongly recommended (`setup.ps1`).

## Related Projects

`pi_scripts/` contains **separate codebase for Raspberry Pi** (runs on ROV, not Ground Station):

- Python scripts for camera streaming, MAVProxy, sensor servers
- Bash scripts for autostart and service management
- These run on Raspbian/Linux, not Windows

Don't confuse Pi scripts with Ground Station code when editing.
