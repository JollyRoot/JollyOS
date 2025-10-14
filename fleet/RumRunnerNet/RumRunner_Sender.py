#!/usr/bin/env python3
"""
RumRunner_Sender — sends a small packet to RumRunner_Receiver
for proof of concept over TCP.
"""

import socket, time

HOST = "raspberrypi4.local"   # or IP like "192.168.1.42"
PORT = 5005

def main():
    msg = f"Ahoy from RumRunner_Sender at {time.time()}"
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[net] connecting to {HOST}:{PORT} ...")
        s.connect((HOST, PORT))
        s.sendall(msg.encode("utf-8"))
        print(f"[net] sent: {msg}")
        reply = s.recv(1024).decode("utf-8")
        print(f"[net] reply: {reply}")

if __name__ == "__main__":
    main()
