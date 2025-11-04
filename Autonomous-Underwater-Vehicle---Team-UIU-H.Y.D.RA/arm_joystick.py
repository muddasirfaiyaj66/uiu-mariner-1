# # laptop_joystick_client.py
# import pygame
# import socket
# import time

# # Jetson IP and Port
# JETSON_IP = "10.42.0.26"  # 🔁 Replace with your Jetson's IP
# PORT = 5005

# # Set up socket
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# # Joystick setup
# pygame.init()
# pygame.joystick.init()

# if pygame.joystick.get_count() == 0:
#     print("No joystick detected.")
#     exit()

# joystick = pygame.joystick.Joystick(0)
# joystick.init()
# print(f"Connected to joystick: {joystick.get_name()}")

# # Button to command mapping
# button_command_map = {
#     0: "1c",        # A
#     1: "2c",       # B
#     2: "3c",        # X
#     3: "4c",       # Y
#     4: "5c",        # LB
#     5: "5ac",       # RB
#     6: "startCamera",  # Back
#     7: "allstop",      # Start
 
# }
  
# # Track state to avoid repeated sends
# button_states = [0] * joystick.get_numbuttons()
# last_hat = (0, 0)

# try:
#     while True:
#         pygame.event.pump()

#         # Check buttons
#         for btn_index, command in button_command_map.items():
#             is_pressed = joystick.get_button(btn_index)

#             if is_pressed and not button_states[btn_index]:
#                 print(f"Sending command: {command}")
#                 sock.sendto(command.encode(), (JETSON_IP, PORT))

#             button_states[btn_index] = is_pressed

#         # Check D-pa(hat) input (if applicable)
#         hat = joystick.get_hat(0)
#         if hat != last_hat:
#             if hat == (0, 1):  # Up
#                 print("D-pad Up → Sending 4ac")
#                 sock.sendto("4ac".encode(), (JETSON_IP, PORT))
#             elif hat == (0, -1):  # Down
#                 print("D-pad Down → Sending 1ac")
#                 sock.sendto("1ac".encode(), (JETSON_IP, PORT))
#             elif hat == (-1, 0):  # Left
#                 print("D-pad Left → Sending 3ac")
#                 sock.sendto("3ac".encode(), (JETSON_IP, PORT))
#             elif hat == (1, 0):  # Right
#                 print("D-pad Right → Sending 2ac")
#                 sock.sendto("2ac".encode(), (JETSON_IP, PORT))
#             last_hat = hat

#         time.sleep(0.1)

# except KeyboardInterrupt:
#     print("Exiting...")

# finally:
#     pygame.quit()







# laptop_joystick_client.py
import pygame
import socket
import time
import sys

# Jetson IP and Port
JETSON_IP = "10.42.0.186"
PORT = 5005

# Set up socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Joystick setup
pygame.init()
pygame.joystick.init()

# Target joystick name
TARGET_JOYSTICK_NAME = "Xbox 360 Controller"

# Find the joystick
target_joystick = None
for i in range(pygame.joystick.get_count()):
    js = pygame.joystick.Joystick(i)
    js.init()
    print(f"Detected joystick: {js.get_name()}")

    if TARGET_JOYSTICK_NAME in js.get_name():
        target_joystick = js
        print(f"✅ Found target joystick: {js.get_name()}")
        break

if not target_joystick:
    print("❌ Target joystick not found. Exiting.")
    sys.exit()

# Button to command mapping
button_command_map = {
    0: "1c",        # A
    1: "2c",        # B
    2: "3c",        # X
    3: "4c",        # Y
    4: "5c",        # LB
    5: "5ac",       # RB
    6: "startCamera",  # Back
    7: "allstop",      # Start
}

# Track state to avoid repeated sends
button_states = [0] * target_joystick.get_numbuttons()
last_hat = (0, 0)

try:
    while True:
        pygame.event.pump()

        # Check buttons
        for btn_index, command in button_command_map.items():
            is_pressed = target_joystick.get_button(btn_index)

            if is_pressed and not button_states[btn_index]:
                print(f"Sending command: {command}")
                sock.sendto(command.encode(), (JETSON_IP, PORT))

            button_states[btn_index] = is_pressed

        # Check D-pad (hat) input
        hat = target_joystick.get_hat(0)
        if hat != last_hat:
            if hat == (0, 1):  # Up
                print("D-pad Up → Sending 4ac")
                sock.sendto("4ac".encode(), (JETSON_IP, PORT))
            elif hat == (0, -1):  # Down
                print("D-pad Down → Sending 1ac")
                sock.sendto("1ac".encode(), (JETSON_IP, PORT))
            elif hat == (-1, 0):  # Left
                print("D-pad Left → Sending 3ac")
                sock.sendto("3ac".encode(), (JETSON_IP, PORT))
            elif hat == (1, 0):  # Right
                print("D-pad Right → Sending 2ac")
                sock.sendto("2ac".encode(), (JETSON_IP, PORT))
            last_hat = hat

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Exiting...")

finally:
    pygame.quit()
