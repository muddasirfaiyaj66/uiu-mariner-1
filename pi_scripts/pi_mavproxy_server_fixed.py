#!/usr/bin/env python3
"""
Simple MAVLink TCP Relay Server - UIU MARINER
Forwards MAVLink messages between serial Pixhawk and TCP clients.

THIS IS A FIXED VERSION that properly handles message relaying.
"""

import socket
import threading
import time
import sys
from pathlib import Path
from pymavlink import mavutil

class MAVLinkTCPRelay:
    """Simple MAVLink TCP relay that actually works"""

    def __init__(self, serial_port="/dev/ttyAMA0", baud=57600, tcp_host="0.0.0.0", tcp_port=7000):
        self.serial_port = serial_port
        self.baud = baud
        self.tcp_host = tcp_host
        self.tcp_port = tcp_port
        self.pixhawk = None
        self.server_socket = None
        self.clients = []
        self.clients_lock = threading.Lock()
        self.running = True
        self._message_buffer = b""
        self._buffer_lock = threading.Lock()

    def connect_pixhawk(self):
        """Connect to Pixhawk via serial"""
        print(f"\n[PIXHAWK] Connecting to {self.serial_port} @ {self.baud} baud...")
        try:
            self.pixhawk = mavutil.mavlink_connection(
                self.serial_port,
                baud=self.baud,
                autoreconnect=True,
            )
            hb = self.pixhawk.wait_heartbeat(timeout=5)
            if hb:
                print(f"[OK] Pixhawk connected on {self.serial_port}!")
                return True
            else:
                print(f"[ERROR] No heartbeat from Pixhawk")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to connect to Pixhawk: {e}")
            return False

    def start_tcp_server(self):
        """Start TCP server for Ground Station connections"""
        print(f"\n[SERVER] Starting TCP server on {self.tcp_host}:{self.tcp_port}...")
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((self.tcp_host, self.tcp_port))
            self.server_socket.listen(5)
            print(f"[OK] TCP server listening on {self.tcp_host}:{self.tcp_port}")
            
            # Start accepting connections in background
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start TCP server: {e}")
            return False

    def _accept_connections(self):
        """Accept incoming TCP connections"""
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"[CLIENT] Connected from {addr}")
                with self.clients_lock:
                    self.clients.append(conn)
                
                # Handle client in separate thread
                threading.Thread(
                    target=self._handle_client,
                    args=(conn, addr),
                    daemon=True
                ).start()
            except Exception as e:
                if self.running:
                    print(f"[SERVER] Accept error: {e}")

    def _handle_client(self, conn, addr):
        """Handle a single client connection"""
        try:
            conn.settimeout(2)
            while self.running:
                try:
                    # Receive from client (commands to Pixhawk)
                    data = conn.recv(1024)
                    if not data:
                        print(f"[CLIENT] Connection closed by {addr}")
                        break
                    
                    # Forward to Pixhawk
                    if self.pixhawk:
                        try:
                            self.pixhawk.write(data)
                        except:
                            pass
                except socket.timeout:
                    # No data received - that's OK
                    pass
                except:
                    break
        except:
            pass
        finally:
            with self.clients_lock:
                if conn in self.clients:
                    self.clients.remove(conn)
            try:
                conn.close()
            except:
                pass
            print(f"[CLIENT] Disconnected: {addr}")

    def relay_messages(self):
        """Main relay loop - read from Pixhawk and send to all clients"""
        print("\n[RELAY] Starting message relay...")
        hb_count = 0
        last_hb_log = time.time()

        while self.running:
            try:
                if not self.pixhawk:
                    time.sleep(0.1)
                    continue

                # Read message from Pixhawk
                msg = self.pixhawk.recv_match(blocking=False, timeout=0.01)
                
                if msg:
                    # Encode message for transmission
                    try:
                        # The pymavlink message object has a _msgbuf attribute with the raw bytes
                        msg_bytes = msg._msgbuf
                        
                        if msg_bytes:
                            # Send to all connected clients
                            with self.clients_lock:
                                dead_clients = []
                                for client in self.clients:
                                    try:
                                        client.sendall(bytes(msg_bytes))
                                    except:
                                        dead_clients.append(client)
                                
                                # Remove dead clients
                                for client in dead_clients:
                                    self.clients.remove(client)
                                    try:
                                        client.close()
                                    except:
                                        pass
                            
                            # Log heartbeats periodically
                            if msg.get_type() == "HEARTBEAT":
                                hb_count += 1
                                if time.time() - last_hb_log > 5:
                                    print(f"[RELAY] Forwarded {hb_count} heartbeats to {len(self.clients)} clients")
                                    hb_count = 0
                                    last_hb_log = time.time()
                    except Exception as e:
                        print(f"[RELAY] Error: {e}")
                else:
                    time.sleep(0.001)  # Small delay

            except Exception as e:
                print(f"[RELAY] Error: {e}")
                time.sleep(0.1)

    def run(self):
        """Main entry point"""
        print("=" * 60)
        print("MAVLink TCP RELAY SERVER - UIU MARINER (FIXED)")
        print("=" * 60)
        print(f"Serial: {self.serial_port} @ {self.baud} baud")
        print(f"TCP: {self.tcp_host}:{self.tcp_port}")
        print("=" * 60)

        try:
            if not self.connect_pixhawk():
                print("[ERROR] Failed to connect to Pixhawk")
                return False

            if not self.start_tcp_server():
                print("[ERROR] Failed to start TCP server")
                return False

            # Start relay (blocks)
            self.relay_messages()

        except KeyboardInterrupt:
            print("\n[SERVER] Shutting down...")
        except Exception as e:
            print(f"[ERROR] Fatal: {e}")
            return False

        self.running = False
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="MAVLink TCP Relay")
    parser.add_argument("--master", default="/dev/ttyAMA0", help="Serial port")
    parser.add_argument("--baudrate", type=int, default=57600, help="Baud rate")
    parser.add_argument("--port", type=int, default=7000, help="TCP port")
    args = parser.parse_args()

    relay = MAVLinkTCPRelay(
        serial_port=args.master,
        baud=args.baudrate,
        tcp_port=args.port
    )
    relay.run()
