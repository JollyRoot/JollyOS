#!/usr/bin/env python3
"""
RumRunner_Receiver — listens for incoming RumLine packets
and replies to confirm link-up.
"""
import sys, os
sys.path.append(os.path.expanduser("~/Desktop/JollyOS"))

import socket
from fleet.shared import RumLine  # shared protocol layer

from fleet.SpyGlass.Lidar import TfLunaTest
HOST = "0.0.0.0"
PORT = 5005

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        print(f"[net] RumRunner_Receiver listening on {HOST}:{PORT} ...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[net] connection from {addr}")
                data = conn.recv(4096)
                if not data:
                    continue

                try:
                    packet = RumLine.decode(data)
                    ship = packet.get("ship", "Unknown")
                    payload = packet.get("payload", {})
                    print(f"[recv] {ship} reports: {payload}")
                except Exception as e:
                    print(f"[error] could not decode packet: {e}")
                    print(f"[raw] {data!r}")

                conn.sendall(b"Aye, message received loud and clear!")

if __name__ == "__main__":
    main()

