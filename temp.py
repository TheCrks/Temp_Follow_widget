import tkinter as tk
import subprocess
import threading

# Function to get all temperature data from sensors
def get_all_temp_data():
    # Run the sensors command to fetch all the sensor information
    try:
        sensors_output = subprocess.check_output(['sensors']).decode().splitlines()
    except subprocess.CalledProcessError:
        return []

    temp_data = []
    names = ['CPU: ', 'Core 0: ', 'Core 1: ', 'Core 2: ', 'Core 3: ', 'PCH: ', 'Wifi Module: ', 'SSD: ', 'Pass', 'ACPI: ']
    index = 0
    # Process the sensors output and extract temperature information
    for line in sensors_output:
        if '°C' in line:
            if index != 8:  
                temp_value = line.strip().split('°C')[0].split('+')[1]
                try:
                    temp_data.append((names[index] + temp_value + "°C", float(temp_value)))
                except ValueError:
                    pass  # Skip invalid values if any
            index += 1
    
    # Get GPU temperature using nvidia-smi
    try:
        nvidia_smi = subprocess.check_output(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'])
        gpu_temp = float(nvidia_smi.decode().strip())
        temp_data.append((f"GPU Temp: {gpu_temp}°C", gpu_temp))
    except subprocess.CalledProcessError:
        gpu_temp = "N/A"
        temp_data.append((gpu_temp, 0))
    
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
            if temp == 0:  # For N/A
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
