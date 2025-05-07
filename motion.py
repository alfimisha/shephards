import serial
import serial.tools.list_ports
import time
import math
import os
import pickle
import numpy as np
from pynput import keyboard  # Replaced keyboard library
from tslearn.metrics import dtw
from sklearn.neighbors import KNeighborsClassifier

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

# === Model Functions ===

MODEL_PATH = "motion_model.pkl"

def save_baseline(baseline_data):
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(baseline_data, f)

def load_baseline():
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    return None

# === Main Program ===

dist = []
filtered_ports = list_ports()

if len(filtered_ports) > 1:
    ser0 = serial.Serial(filtered_ports[0], 9600, timeout=1)
    ser1 = serial.Serial(filtered_ports[1], 9600, timeout=1)
    print(f"Connected to:\n  Port 0: {filtered_ports[0]}\n  Port 1: {filtered_ports[1]}")

    baseline_data = load_baseline()

    stop_flag = [False]  # Use a list to simulate a mutable flag

    def on_press(key):
        if hasattr(key, 'char') and key.char == 'q':  # Check if the 'q' key is pressed
            stop_flag[0] = True  # Set the flag to stop the loop
            print("\n'q' detected. Exiting loop and preparing training or inference...")

    # Start listening for key events in a separate thread
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

    try:
        while not stop_flag[0]:
            port0_lines = []
            port1_lines = []

            # Collect data from port0
            while len(port0_lines) < 3:
                if ser0.in_waiting:
                    line = ser0.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port0_lines.append(line)

            # Collect data from port1
            while len(port1_lines) < 3:
                if ser1.in_waiting:
                    line = ser1.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        port1_lines.append(line)

            # Compute average acceleration from port0 data
            port0_str = "\n".join(port0_lines)
            avg_acc = find_avg_acc_val(port0_str)
            avg_float = avg_acc.to_float() / 500  # Normalize by 500 or whatever fits your data

            if avg_float != 0:
                dist.append(avg_float)

            print(f"Latest avg: {avg_float:.3f} | dist len: {len(dist)}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Stopping via Ctrl+C...")

    ser0.close()
    ser1.close()

    dist_np = np.array(dist).reshape(-1, 1)

    if baseline_data is None:
        # First time running: Save baseline data
        print("No baseline found. Saving current motion as baseline.")
        save_baseline(dist_np)
        print("Baseline saved.")
    else:
        # Compare the new data with the baseline using DTW
        print("Baseline loaded. Comparing current motion with baseline.")
        dist_dtw = dtw(baseline_data, dist_np)
        print(f"DTW distance: {dist_dtw}")

        # Define a threshold for similarity
        similarity_threshold = 1000  # This can be adjusted based on your needs

        if dist_dtw < similarity_threshold:
            print("✅ Movement is similar to baseline.")
        else:
            print("⚠️ Movement deviates from baseline.")
else:
    print("Not enough USB modem ports found.")
