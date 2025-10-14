#!/usr/bin/env python3
"""
start_spyglass_rumrunner.py — unified startup sequence for the Pi Zero.
Runs the TF-Luna reader and RumRunnerNet sender together in one process.
"""

import sys, os, time, threading

sys.path.append(os.path.expanduser("~/Desktop/JollyOS"))

from fleet.SpyGlass.Lidar import TfLunaTest
from fleet.RumRunnerNet import RumRunner_Sender


def main():
    print("[launch] SpyGlass + RumRunnerNet unified startup initiated…")

    # 1. Start SpyGlass (TF-Luna) in a background thread
    print("[launch] Starting SpyGlass LiDAR reader thread…")
    lidar_thread = threading.Thread(
        target=TfLunaTest.main, daemon=True, name="SpyGlassLidar"
    )
    lidar_thread.start()

    # 2. Give LiDAR a few seconds to warm up
    for i in range(3, 0, -1):
        print(f"[launch] Waiting {i}s for SpyGlass to initialize…")
        time.sleep(1)

    # 3. Start RumRunnerNet sender (runs until stopped)
    print("[launch] Starting RumRunnerNet sender loop…")
    try:
        RumRunner_Sender.main()
    except KeyboardInterrupt:
        print("\n[shutdown] Manual interrupt received — closing systems.")


if __name__ == "__main__":
    main()
