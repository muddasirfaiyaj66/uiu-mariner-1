import subprocess
import socket
import threading
import signal
import os

HOST = "0.0.0.0"
PORT = 9000
DEST_IP = "192.168.190.159"
DEST_PORT = "5000"

current_proc = None
current_cam = 0  # Start with camera 0

def start_stream(cam_index):
    global current_proc
    stop_stream()
    print(f"Starting stream with camera {cam_index}")
    cmd = f"libcamera-vid --camera {cam_index} -t 0 --inline -n --width 1280 --height 720 --framerate 30 " \
          f"--codec h264 --libav-format h264 -o - | gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 " \
          f"pt=96 ! udpsink host={DEST_IP} port={DEST_PORT}"
    current_proc = subprocess.Popen(cmd, shell=True, preexec_fn=os.setsid)

def stop_stream():
    global current_proc
    if current_proc:
        print("Stopping current stream")
        os.killpg(os.getpgid(current_proc.pid), signal.SIGTERM)
        current_proc = None

def client_handler(conn):
    global current_cam
    while True:
        data = conn.recv(1024).decode().strip()
        if not data:
            break
        if data == "SWITCH":
            current_cam = 1 - current_cam  # Toggle between 0 and 1
            start_stream(current_cam)
    conn.close()

def main():
    start_stream(current_cam)  # Start with cam 0
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"Server listening on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"Connection from {addr}")
            threading.Thread(target=client_handler, args=(conn,), daemon=True).start()

if __name__ == "__main__":
    main()
