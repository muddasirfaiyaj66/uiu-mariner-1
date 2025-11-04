#!/usr/bin/env python3
"""
MAVProxy Server for Raspberry Pi
Provides socket interface to MAVProxy for remote control
Based on tested code from Pi Codes/pixhawkserver.py
"""

import socket
import subprocess
import sys


def start_mavproxy_server(
    mavproxy_master="/dev/ttyACM0",
    baudrate=115200,
    server_host="0.0.0.0",
    server_port=7000,
):
    """
    Start MAVProxy and provide TCP socket interface.

    Args:
        mavproxy_master: Serial device path for Pixhawk connection
        baudrate: Serial baud rate
        server_host: Server bind address
        server_port: TCP port for client connections
    """
    print("=" * 60)
    print("MAVPROXY SERVER - UIU MARINER")
    print("=" * 60)
    print(f"MAVLink: {mavproxy_master} @ {baudrate} baud")
    print(f"Server: {server_host}:{server_port}")
    print("=" * 60)

    # Start MAVProxy process
    print("\n[MAVPROXY] Starting MAVProxy...")
    mavproxy_cmd = [
        "mavproxy.py",
        f"--master={mavproxy_master}",
        "--baudrate",
        str(baudrate),
    ]

    mavproxy_process = subprocess.Popen(
        mavproxy_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )

    print("[MAVPROXY] ✅ MAVProxy started")

    # Create TCP server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((server_host, server_port))
    server_socket.listen(5)

    print(f"\n[SERVER] 🚀 Listening on {server_host}:{server_port}")
    print("[SERVER] Waiting for Ground Station connection...")

    try:
        while True:
            conn, addr = server_socket.accept()
            print(f"\n[SERVER] ✅ Connected to {addr}")

            try:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        print("[SERVER] ⚠️ Connection closed by client")
                        break

                    command = data.decode().strip()
                    print(f"[COMMAND] Received: {command}")

                    # Forward command to MAVProxy
                    try:
                        mavproxy_process.stdin.write(command + "\n")
                        mavproxy_process.stdin.flush()
                        print(f"[COMMAND] ✅ Sent to MAVProxy")
                    except Exception as e:
                        print(f"[COMMAND] ❌ Error forwarding: {e}")

            except Exception as e:
                print(f"[SERVER] ❌ Connection error: {e}")
            finally:
                conn.close()
                print("[SERVER] Connection closed, waiting for new connection...")

    except KeyboardInterrupt:
        print("\n\n[SERVER] Shutting down...")
    finally:
        server_socket.close()
        mavproxy_process.terminate()
        mavproxy_process.wait()
        print("[SERVER] Server stopped")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="MAVProxy TCP Server for ROV")
    parser.add_argument(
        "--master",
        type=str,
        default="/dev/ttyACM0",
        help="MAVLink serial device (default: /dev/ttyACM0)",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Serial baud rate (default: 115200)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Server bind address (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--port", type=int, default=7000, help="TCP server port (default: 7000)"
    )

    args = parser.parse_args()

    try:
        start_mavproxy_server(
            mavproxy_master=args.master,
            baudrate=args.baudrate,
            server_host=args.host,
            server_port=args.port,
        )
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
