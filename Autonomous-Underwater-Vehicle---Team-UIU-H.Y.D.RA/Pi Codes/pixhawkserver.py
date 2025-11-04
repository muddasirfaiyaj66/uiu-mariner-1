import socket
import subprocess

HOST = "0.0.0.0"  # Listen on all interfaces
PORT = 7000       # Choose any free port

# Start MAVProxy in the background
mavproxy_process = subprocess.Popen(
    ["mavproxy.py", "--master=/dev/serial0", "--baudrate", "57600"],
    stdin=subprocess.PIPE,
    text=True
)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Listening on {HOST}:{PORT}...")

    while True:
        conn, addr = server_socket.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                command = data.decode().strip()
                print(f"Received: {command}")
                mavproxy_process.stdin.write(command + "\n")
                mavproxy_process.stdin.flush()
