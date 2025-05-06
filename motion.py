import serial
import serial.tools.list_ports
import time

def list_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports if 'usbmodem' in port.device]

filtered_ports = list_ports()

if len(filtered_ports) > 1:
    port0 = filtered_ports[0]
    ser0 = serial.Serial(port0, 9600, timeout=1)
    print(f"Port 0: {port0}")

    port1 = filtered_ports[1]
    ser1 = serial.Serial(port1, 9600, timeout=1)
    print(f"Port 1: {port1}")

    try:
        while True:
            port0_lines = []
            port1_lines = []

            # Collect 3 complete lines from port0
            while len(port0_lines) < 3:
                if ser0.in_waiting:
                    line = ser0.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port0_lines.append(line)

            # Collect 1 complete line from port1
            while len(port1_lines) < 3:
                if ser1.in_waiting:
                    line = ser1.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port1_lines.append(line)
            # Print all at once
            for line in port0_lines:
                print("port0:", line)
            print ("." * 100)
            for line in port0_lines:
                print("port1:", line)
            
            print("-" * 50)  # separator for readability

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Exiting program.")
        ser0.close()
        ser1.close()
else:
    print("Not enough ports found.")
