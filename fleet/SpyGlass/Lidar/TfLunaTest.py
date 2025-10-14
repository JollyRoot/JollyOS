# tf_luna_fast.py
import serial, time, collections

PORT = '/dev/serial0'
BAUD = 115200
MIN_STRENGTH = 50
WINDOW = 5
PRINT_EVERY = 5

latest_avg = None

def get_latest_avg():
    global latest_avg
    return latest_avg

def read_frame(ser):
    head = ser.read(2)
    if head != b'\x59\x59':
        return None
    frame = head + ser.read(7)
    if len(frame) != 9:
        return None
    if (sum(frame[:8]) & 0xFF) != frame[8]:
        return None
    dist = frame[2] + (frame[3] << 8)
    strength = frame[4] + (frame[5] << 8)
    temp_c = (frame[6] + (frame[7] << 8)) / 8 - 256
    return dist, strength, temp_c

def main():
    global latest_avg
    ser = serial.Serial(PORT, BAUD, timeout=0.05)
    buf = collections.deque(maxlen=WINDOW)
    print("TF-Luna fast reader started…")
    while True:
        rec = read_frame(ser)
        if not rec:
            continue
        dist, strength, temp_c = rec
        if strength < MIN_STRENGTH:
            continue
        buf.append(dist)
        avg = sum(buf)/len(buf)
        latest_avg = int(avg)


if __name__ == "__main__":
    main()

