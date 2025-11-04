import smbus
import time
import socket

# I2C bus 0 (used in your case)
bus = smbus.SMBus(0)

# BMP388 I2C address
BMP388_ADDR = 0x77

# Registers for BMP388
BMP388_TEMP_REG = 0x04
BMP388_PRESS_REG = 0x07
BMP388_ALT_REG = 0x08

# Sensor initialization
def initialize_sensor():
    bus.write_byte_data(BMP388_ADDR, 0x1B, 0xB6)  # Soft reset
    time.sleep(0.5)
    bus.write_byte_data(BMP388_ADDR, 0x1B, 0x33)  # Normal mode
    time.sleep(0.5)

# Read I2C data function
def read_data(register):
    return bus.read_i2c_block_data(BMP388_ADDR, register, 3)

# Read temperature
def read_temperature():
    temp_data = bus.read_i2c_block_data(BMP388_ADDR, BMP388_TEMP_REG, 2)
    raw_temp = (temp_data[1] << 8) | temp_data[0]  
    return raw_temp / 256.0  # Convert to Celsius

# Read pressure
def read_pressure():
    data = read_data(BMP388_PRESS_REG)
    pressure_raw = (data[0] | (data[1] << 8) | (data[2] << 16))
    return pressure_raw / 256.0  

# Read altitude
def read_altitude():
    data = read_data(BMP388_ALT_REG)
    altitude_raw = (data[0] | (data[1] << 8) | (data[2] << 16))
    return altitude_raw / 100.0  

# **Socket Server Setup**
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("0.0.0.0", 7000))  # Listen on all interfaces, port 5000
    server.listen(1)
    print("Waiting for PyQt6 client connection...")
    
    conn, addr = server.accept()
    print(f"Connection established with {addr}")

    try:
        initialize_sensor()
        while True:
            temperature = read_temperature()
            pressure = read_pressure()
            altitude = read_altitude()

            data_string = f"{temperature},{pressure},{altitude}\n"
            conn.sendall(data_string.encode())  # Send data to PyQt6 client

            time.sleep(1)  # Send data every second
    except KeyboardInterrupt:
        print("Server shutting down.")
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    start_server()
