import serial
import time
import numpy as np
import csv
import os  # Added for file checking
from datetime import datetime

# The Math: Stull Formula for Wet Bulb
def get_wet_bulb(t, rh):
    twb = (t * np.arctan(0.151977 * (rh + 8.313659)**0.5) + 
           np.arctan(t + rh) - np.arctan(rh - 1.676331) + 
           0.00391838 * (rh**1.5) * np.arctan(0.023101 * rh) - 4.686035)
    return round(twb, 2)

# --- HEADER LOGIC ---
file_path = 'weather_data.csv'
# If the file doesn't exist, create it and add the header row
if not os.path.isfile(file_path):
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Timestamp', 'Temperature', 'Humidity', 'Wet_Bulb'])
    print("Created fresh CSV with headers.")

# Open the connection to your Arduino
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
    time.sleep(2) 
    print("Connected to Arduino! Logging 1-minute intervals...")
except:
    print("Error: Could not open /dev/ttyUSB0. Is the Serial Monitor still open?")
    exit()

try:
    while True:
        ser.reset_input_buffer()
        time.sleep(2.1) 

        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            
            if "Humidity" in line:
                try:
                    parts = line.split('|')
                    h = float(parts[0].split(':')[1].replace('%', '').strip())
                    t = float(parts[1].split(':')[1].replace('°C', '').strip())
                    
                    wb = get_wet_bulb(t, h)
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Temp: {t}°C | Hum: {h}% | WET BULB: {wb}°C")

                    # Log to CSV (Append mode)
                    with open(file_path, mode='a', newline='') as file:
                        writer = csv.writer(file)
                        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), t, h, wb])
                
                except (ValueError, IndexError):
                    print("Skipping a glitchy reading...")
                    continue
                
                # Sleep for 60 seconds for the 1-minute interval
                time.sleep(60)

except KeyboardInterrupt:
    print("\nLogging stopped.")
    ser.close()