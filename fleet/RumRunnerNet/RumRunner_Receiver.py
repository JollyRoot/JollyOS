#!/usr/bin/env python3
"""
RumRunner_Receiver — listens for RumRunner_Sender
and replies to confirm link-up.
"""

import socket

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
                data = conn.recv(1024)
                if not data:
                    continue
                msg = data.decode("utf-8")
                print(f"[recv] {msg}")
                conn.sendall(b"Aye, message received loud and clear!")

if __name__ == "__main__":
    main()
