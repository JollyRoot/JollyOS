#!/usr/bin/env python3
"""
RumLine — the shared communication format for JollyOS Fleet.
Used by RumRunnerNet, SpyGlass, and future modules.
"""

import time, json

def cast_message(ship_name, data):
    """
    Build a standardized packet for transmission.
    Example: cast_message("SpyGlass", {"distance": 124})
    """
    return {
        "ship": ship_name,
        "timestamp": time.time(),
        "payload": data
    }

def encode(packet: dict) -> bytes:
    """Convert packet dict to bytes for network send."""
    return json.dumps(packet).encode('utf-8')

def decode(raw: bytes) -> dict:
    """Convert bytes back to a Python dict."""
    return json.loads(raw.decode('utf-8'))
