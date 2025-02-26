import tkinter as tk
import subprocess
import threading
import clr  # You need to install pythonnet to use this (pip install pythonnet)
from System import *
from OpenHardwareMonitor import *

# Function to get all temperature data from sensors
def get_all_temp_data():
    # Run the sensors command to fetch GPU temperature using nvidia-smi
    try:
        nvidia_smi = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'])
        gpu_temp = float(nvidia_smi.decode().strip())
    except subprocess.CalledProcessError:
        gpu_temp = "N/A"

    # Initialize OpenHardwareMonitor and get CPU and other temperature data
    temp_data = []
    try:
        # Load OpenHardwareMonitorLib.dll (Ensure OpenHardwareMonitor is in the same directory as your script)
        clr.AddReference(r"OpenHardwareMonitor\OpenHardwareMonitorLib.dll")
        from OpenHardwareMonitor.Hardware import Computer

        # Initialize Computer object and update hardware data
        computer = Computer()
        computer.Open()
        computer.AcceptsUserMode = True
        computer.Hardware[0].Update()

        # Extract CPU temperature
        for hardware in computer.Hardware:
            if hardware.HardwareType == HardwareType.CPU:
                for sensor in hardware.Sensors:
                    if sensor.SensorType == SensorType.Temperature:
                        temp_data.append((f"{sensor.Name}: {sensor.Value}°C", sensor.Value))

    except Exception as e:
        temp_data.append((f"Error fetching data: {str(e)}", 0))

    # Add GPU temperature to the data
    temp_data.append((f"GPU Temp: {gpu_temp}°C", gpu_temp))

    return temp_data

# Function to update the data in the GUI
def update_data():
    temp_data = get_all_temp_data()

    # Clear the existing text
    for label in temp_labels:
        label.config(text="", bg="white")
    
    # Update the labels with the new temperature data
    for i, (data, temp) in enumerate(temp_data):
        if i < len(temp_labels):
            temp_labels[i].config(text=data)
            # Change color based on the temperature
            if temp == 0:  # For N/A or error
                temp_labels[i].config(bg="white")
            elif temp < 50:
                temp_labels[i].config(bg="lightgreen")  # Cool
            elif 50 <= temp < 75:
                temp_labels[i].config(bg="yellow")  # Warning
            else:
                temp_labels[i].config(bg="red")  # Hot

    # Refresh every second
    window.after(1000, update_data)

# Creating the main window
window = tk.Tk()
window.title("Temperature Monitor")

# Create a list to store labels for each temperature data
temp_labels = []

# Initializing 10 labels to display the temperature data
for _ in range(10):
    label = tk.Label(window, font=("Helvetica", 10), text="", width=40, height=2)
    label.pack(pady=2)
    temp_labels.append(label)

# Start updating the data
update_data()

# Run the GUI loop
window.mainloop()
