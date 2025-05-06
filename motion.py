import serial
import serial.tools.list_ports
import time
#filter all the needed ports
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
            port0_str = ""
            port1_str = ""

            # Read all available bytes from port0
            while ser0.in_waiting > 0:
                port0_str += ser0.read().decode('utf-8', errors='ignore')

            if port0_str:
                print("port0:", port0_str.strip())
                

            # Read all available bytes from port1
            while ser1.in_waiting > 0:
                port1_str += ser1.read().decode('utf-8', errors='ignore')

            

            if port1_str:
                print("port1:", port1_str.strip())

                time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting program.")
        ser0.close()
        ser1.close()
else:
    print("No ports found.")
