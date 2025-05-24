"""
 * @file graphs.py
 * @date 17/5/2025
 * @author Hector Tovar
 * 
 * @brief this script visualizes real-time data from a tractor telemetry system using MQTT and PySimpleGUI.
 * This code should be run in a Python environment with the required libraries installed.
 * Also this script should be running in the Raspberry Pi.
"""

import csv
import PySimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import paho.mqtt.client as mqtt

# Initialization
data = []
csv_file = open("tractor_data.csv", "w", newline='')
writer = csv.writer(csv_file)
writer.writerow(["Engine Speed", "Vehicle Speed", "Gear"])

# Configure window
sg.theme("DarkBlue")
layout = [[sg.Text("Real-Time Data Visualization")],
          [sg.Canvas(key="-CANVAS-")],
          [sg.Button("Exit")]]
window = sg.Window("Tractor Telemetry", layout, finalize=True)

# Plot
fig, ax = plt.subplots()
line1, = ax.plot([], [], label="Engine Speed")
line2, = ax.plot([], [], label="Vehicle Speed")
ax.legend()
canvas = FigureCanvasTkAgg(fig, window["-CANVAS-"].TKCanvas)
canvas.draw()
canvas.get_tk_widget().pack()

# Data for plotting
engine_speed, vehicle_speed = [], []

def update_graph():
    line1.set_data(range(len(engine_speed)), engine_speed)
    line2.set_data(range(len(vehicle_speed)), vehicle_speed)
    ax.relim()
    ax.autoscale_view()
    canvas.draw()

# MQTT Callback
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        e_speed, v_speed, gear = map(float, payload.split(","))
        data.append((e_speed, v_speed, gear))
        engine_speed.append(e_speed)
        vehicle_speed.append(v_speed)
        writer.writerow([e_speed, v_speed, int(gear)])
        update_graph()
    except ValueError:
        pass  # Ignore format errors

# MQTT
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("tractor/data")
client.loop_start()

# GUI Loop
while True:
    event, _ = window.read(timeout=100)
    if event == sg.WIN_CLOSED or event == "Exit":
        break

client.loop_stop()
client.disconnect()
csv_file.close()
window.close()
