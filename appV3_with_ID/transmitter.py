import time
import serial

def uart_transmit_test():
    try:
        # Use /dev/serial0 for hardware UART
        ser = serial.Serial('/dev/ttyS0', baudrate=9600, timeout=1)
        print("UART TX Test Started. Sending messages every 2 seconds...")

        while True:
            message = "\r\n66\r\n"  # Example message
            ser.write(message.encode())
            print(f"Sent: {message.strip()}")
            time.sleep(2)

    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")

    except KeyboardInterrupt:
        print("Stopped by user.")

    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Serial port closed.")

if __name__ == "__main__":
    uart_transmit_test()