# Sensor Data Display Fix

## Issues Found

### 1. **Port Conflict** ❌

- **Problem**: Camera streams use UDP ports 5000 and 5001
- **Conflict**: Sensor server was also using TCP port 5000
- **Impact**: Sensor data couldn't be received properly due to port binding conflict

### 2. **Text Format Mismatch** ❌

- **Problem**: UI labels initialized with format "0.0 m", "0.0°C", "0.0 hPa"
- **Issue**: Update function used format "Depth: 0.0 m", "Temp: 0.0 °C", "Pressure: 0.0 hPa"
- **Impact**: Text didn't update properly in the UI labels

### 3. **No Debug Output** ❌

- **Problem**: No console output to verify data flow
- **Impact**: Couldn't diagnose if sensor worker was receiving data

## Fixes Applied

### ✅ 1. Changed Sensor Port

**File**: `config.json`

```json
"sensors": {
  "host": "raspberrypi.local",
  "port": 5002,  // Changed from 5000 to 5002
  "protocol": "tcp",
  "mock_mode": true,  // Temporarily enabled for testing
  "auto_connect": true
}
```

### ✅ 2. Updated Pi Sensor Server

**File**: `pi_scripts/pi_sensor_server.py`

- Changed default port from 5000 to 5002
- Updated documentation

### ✅ 3. Fixed Text Formatting

**File**: `src/ui/marinerApp.py` - `update_sensor_display()`

```python
# Before:
self.lblDepth.setText(f"Depth: {data['depth']:.1f} m")
self.lblTemperature.setText(f"Temp: {data['temperature']:.1f} °C")
self.lblPressure.setText(f"Pressure: {data['pressure']:.1f} hPa")

# After:
self.lblDepth.setText(f"{data['depth']:.1f} m")
self.lblTemperature.setText(f"{data['temperature']:.1f}°C")
self.lblPressure.setText(f"{data['pressure']:.1f} hPa")
```

### ✅ 4. Added Debug Logging

**Files**: `src/ui/marinerApp.py`, `src/ui/sensorWorker.py`

- Added console output when sensor data is received
- Added console output when UI is updated
- Added debug info for mock sensor data
- Added error handling and stack traces

### ✅ 5. Added UI Force Refresh

**File**: `src/ui/marinerApp.py`

- Added `repaint()` calls to force UI update
- Ensures labels refresh immediately when data arrives

## Testing Steps

### Step 1: Test with Mock Data (Current Configuration)

```powershell
cd "e:\UIU MARINER\mariner-software-1.0"
python launch_mariner.py
```

**Expected Console Output**:

```
[SENSORS] Using mock data (testing mode)
[SENSORS] Connecting signals to UI update methods...
[SENSORS] ✅ Signals connected successfully
[SENSORS] Starting sensor worker thread...
[SENSORS] ✅ Sensor worker thread started
[SENSORS] 🧪 Mock Data: Depth=0.1m, Temp=20.5°C, Pressure=1013.2hPa
[UI] Updating sensor display: Depth=0.1m, Temp=20.5°C, Pressure=1013.2hPa
```

**Expected UI Behavior**:

- Depth value should change continuously (0.0m → 0.1m → 0.2m → ... → 10.0m → back to 0.0m)
- Temperature should fluctuate around 20°C (±2°C)
- Pressure should fluctuate around 1013 hPa (±5 hPa)
- Values update every 500ms

### Step 2: Test with Real Sensor (After Mock Test Works)

1. **Update config.json**:

```json
"sensors": {
  "mock_mode": false  // Change to false
}
```

2. **Update Pi Sensor Server** (SSH to Raspberry Pi):

```bash
# Stop old sensor server if running
sudo pkill -f pi_sensor_server.py

# Update the file from your Ground Station
# (Use update_pi_files.ps1 or manually copy)

# Start new sensor server on port 5002
sudo python3 ~/pi_sensor_server.py --port 5002
```

3. **Verify Pi Sensor Server Output**:

```
[SENSOR] 🚀 Server listening on 0.0.0.0:5002
[SENSOR] Waiting for Ground Station connection...
[SENSOR] ✅ Connected to ('192.168.x.x', xxxxx)
[SENSOR] Sent: T=25.30°C P=101325.00Pa D=0.00m
```

4. **Restart Ground Station Application**:

```powershell
python launch_mariner.py
```

5. **Expected Console Output**:

```
[SENSORS] Connecting to raspberrypi.local:5002 via TCP...
[SENSORS] ✅ TCP connection established
[SENSORS] 📊 Data received: Depth=0.0m, Temp=25.3°C, Pressure=1013.2hPa
[UI] Updating sensor display: Depth=0.0m, Temp=25.3°C, Pressure=1013.2hPa
```

## Port Configuration Summary

| Service     | Protocol | Port     | Notes                          |
| ----------- | -------- | -------- | ------------------------------ |
| Camera 0    | UDP      | 5000     | Primary camera H.264 stream    |
| Camera 1    | UDP      | 5001     | Secondary camera H.264 stream  |
| **Sensors** | **TCP**  | **5002** | **BMP388 sensor data (FIXED)** |
| MAVLink     | TCP      | 7000     | Pixhawk telemetry via MAVProxy |

## Troubleshooting

### Issue: Mock data shows but values don't update

**Check**:

1. Look for console output: `[SENSORS] 🧪 Mock Data: ...`
2. Look for console output: `[UI] Updating sensor display: ...`
3. If first appears but not second, signal connection failed
4. If neither appears, sensor worker thread didn't start

**Solution**: Restart application and check console for errors

### Issue: Real sensor shows "Connected" but displays 0.0

**Check**:

1. Verify Pi sensor server is running on port 5002
2. Check console for: `[SENSORS] 📊 Data received: ...`
3. Check Pi console for: `[SENSOR] Sent: ...`

**Solution**:

- If Pi shows sending but Ground Station not receiving: Check firewall
- If Pi not sending: Check I2C connection to BMP388 sensor
- If receiving but not displaying: Check console for errors

### Issue: Values display as "nan" or invalid

**Check**: Sensor data format from Pi

**Expected Format**: `"temperature,pressure,depth\n"` (CSV)

**Solution**: Verify Pi sensor server is sending correct format

## Next Steps

1. ✅ Test with mock mode (verify UI updates work)
2. ⏳ Update Pi sensor server to use port 5002
3. ⏳ Test with real sensor
4. ⏳ Disable mock mode once confirmed working

## Files Modified

1. `config.json` - Changed sensor port to 5002, enabled mock mode
2. `src/ui/marinerApp.py` - Fixed text formatting, added debugging, added force refresh
3. `src/ui/sensorWorker.py` - Added debugging output
4. `pi_scripts/pi_sensor_server.py` - Changed default port to 5002

---

**Created**: November 4, 2025
**Status**: Ready for testing with mock data
