import serial
import time

port = '/dev/serial0'  # or '/dev/ttyAMA0'
baudrate = 9600
log_file_path = "buffer"

try:
    ser = serial.Serial(port, baudrate, timeout=0.1)
    print("Started reading serial...")

    with open(log_file_path, "a", encoding='utf-8') as log_file:
        while True:
            if ser.in_waiting > 0:
                data = ser.read(ser.in_waiting).decode(errors='ignore')
                print(f"Received: {repr(data)}")  # debug print
                log_file.write(data)
                log_file.flush()
            time.sleep(0.1)

except Exception as e:
    print(f"Error: {e}")
