import RPi.GPIO as GPIO
import socket

# Motor GPIO definitions
motors = {
    "1": {"rpwm": 24, "lpwm": 25},
    "2": {"rpwm": 17, "lpwm": 27},
    "3": {"rpwm": 26,  "lpwm": 19},
    "4": {"rpwm": 22, "lpwm": 4},
    "5": {"rpwm": 16, "lpwm": 20},  # Optional fifth motor
}

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Setup all pins
for motor in motors.values():
    GPIO.setup(motor["rpwm"], GPIO.OUT)
    GPIO.setup(motor["lpwm"], GPIO.OUT)

def rotate_clockwise(motor_id):
    m = motors[motor_id]
    GPIO.output(m["rpwm"], GPIO.HIGH)
    GPIO.output(m["lpwm"], GPIO.LOW)

def rotate_anticlockwise(motor_id):
    m = motors[motor_id]
    GPIO.output(m["rpwm"], GPIO.LOW)
    GPIO.output(m["lpwm"], GPIO.HIGH)

def stop_motor(motor_id):
    m = motors[motor_id]
    GPIO.output(m["rpwm"], GPIO.LOW)
    GPIO.output(m["lpwm"], GPIO.LOW)

def stop_all_motors():
    for motor_id in motors:
        stop_motor(motor_id)

# Setup UDP server
UDP_IP = "0.0.0.0"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"UDP server listening on {UDP_IP}:{UDP_PORT}")

try:
    while True:
        data, addr = sock.recvfrom(1024)
        cmd = data.decode().strip()
        print(f"Received from {addr}: {cmd}")

        if cmd == "allstop":
            stop_all_motors()
            print("All motors stopped.")
            continue

        if len(cmd) >= 2:
            motor_id = cmd[0]
            action = cmd[1:]

            if motor_id not in motors:
                print("Invalid motor ID. Use 1 to 5.")
                continue

            if action == "c":
                rotate_clockwise(motor_id)
                print(f"Motor {motor_id} rotating clockwise.")
            elif action == "ac":
                rotate_anticlockwise(motor_id)
                print(f"Motor {motor_id} rotating anticlockwise.")
            elif action == "stop":
                stop_motor(motor_id)
                print(f"Motor {motor_id} stopped.")
            else:
                print("Invalid command. Use c / ac / stop.")

except KeyboardInterrupt:
    print("Interrupted. Cleaning up GPIO.")
    GPIO.cleanup()

