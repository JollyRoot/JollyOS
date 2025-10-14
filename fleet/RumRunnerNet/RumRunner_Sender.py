#!/usr/bin/env python3
"""
RumRunner_Sender — transmits live SpyGlass LiDAR readings
over RumRunnerNet using the RumLine protocol.
"""

import sys, os, time, socket
sys.path.append(os.path.expanduser("~/Desktop/JollyOS"))

from fleet.shared import RumLine
from fleet.SpyGlass.Lidar import TfLunaTest

HOST = "10.0.0.111"  # Pi 4B Receiver
PORT = 5005

def main():
    print("[rumrunner] sender initialized, starting 1-second loop…")
    while True:
        distance = TfLunaTest.get_latest_avg()
        if distance is None:
            print("[spyglass] waiting for LiDAR data…")
            time.sleep(1)
            continue

        packet = RumLine.cast_message("SpyGlass", {
            "distance_cm": distance,
            "timestamp": time.time()
        })

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2.0)
                s.connect((HOST, PORT))
                s.sendall(RumLine.encode(packet))
                print(f"[net] sent packet: {packet}")
                reply = s.recv(1024)
                if reply:
                    print(f"[net] reply: {reply.decode('utf-8')}")
        except (ConnectionRefusedError, TimeoutError, OSError) as e:
            print(f"[warn] connection failed: {e}")

        time.sleep(1.0)  # one message per second

if __name__ == "__main__":
    main()
