import serial
import serial.tools.list_ports
import time
import math

# === Class & Function Definitions ===

class AccData:
    def __init__(self, x=0.0, y=0.0, z=0.0, is_valid=False):
        self.x = x
        self.y = y
        self.z = z
        self.is_valid = is_valid
    def subtract(self, b):
        return AccData(self.x - b.x, self.y - b.y, self.z - b.z, is_valid=True)
    def add(self, b):
        return AccData(self.x + b.x, self.y + b.y, self.z + b.z, is_valid=True)
    def division(self, divf):
        return AccData(self.x / divf, self.y / divf, self.z / divf, is_valid=True)
    def to_float(self):
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

def find_avg_acc_val(input_str, xLoc=None, yLoc=None, zLoc=None):
    try:
        sum_acc_x = sum_acc_y = sum_acc_z = 0.0
        sum_counter = 0
        lines = input_str.strip().split("\n")
        for line in lines:
            if line.startswith("i"):
                uwbsplit = line.split(",")
                try:
                    sum_acc_x += float(uwbsplit[1])
                    sum_acc_y += float(uwbsplit[2])
                    sum_acc_z += float(uwbsplit[3])
                    sum_counter += 1
                except Exception as ex:
                    print("Error parsing:", line, "|", ex)
        if sum_counter > 0:
            avg_x = sum_acc_x / sum_counter
            avg_y = sum_acc_y / sum_counter
            avg_z = sum_acc_z / sum_counter
            if xLoc is not None: xLoc.append(avg_x)
            if yLoc is not None: yLoc.append(avg_y)
            if zLoc is not None: zLoc.append(avg_z)
            return AccData(avg_x, avg_y, avg_z, is_valid=True)
        else:
            return AccData(0.0, 0.0, 0.0, is_valid=False)
    except Exception as ex1:
        print("General parse error:", ex1)
        print("Input string:", input_str)
        return AccData(0.0, 0.0, 0.0, is_valid=False)

def list_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports if 'usbmodem' in port.device]

# === Main Program ===

dist = []


filtered_ports = list_ports()

if len(filtered_ports) > 1:
    ser0 = serial.Serial(filtered_ports[0], 9600, timeout=1)
    ser1 = serial.Serial(filtered_ports[1], 9600, timeout=1)
    print(f"Connected to:\n  Port 0: {filtered_ports[0]}\n  Port 1: {filtered_ports[1]}")

    try:
        while True:
            port0_lines = []
            port1_lines = []

            # Collect 3 lines from each port
            while len(port0_lines) < 3:
                if ser0.in_waiting:
                    line = ser0.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port0_lines.append(line)

            while len(port1_lines) < 3:
                if ser1.in_waiting:
                    line = ser1.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port1_lines.append(line)

            # Compute avg acceleration from port0
            port0_str = "\n".join(port0_lines)
            avg_acc = find_avg_acc_val(port0_str)
            avg_float = avg_acc.to_float() / 500

            if avg_float != 0:
                dist.append(avg_float)

            # Show output
            print(f"Latest avg: {avg_float:.3f} | dist: {['{:.2f}'.format(d) for d in dist]}")

            time.sleep(0.1)  # small delay

    except KeyboardInterrupt:
        print("Stopping...")
        ser0.close()
        ser1.close()
else:
    print("Not enough USB modem ports found.")
