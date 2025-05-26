"""
 * @file graphs.py
 * @date 17/5/2025
 * @author Hector Tovar
 * 
 * @brief This script visualizes real-time data from a tractor telemetry system using MQTT and matplotlib.
 * It should be run on a Raspberry Pi with the required libraries installed.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt

# --- Data lists ---
timestamps = []
rpms = []
velocidades = []

# --- CSV Setup ---
csv_file = open("tractor_data.csv", "w", newline='')
writer = csv.writer(csv_file)
writer.writerow(["Engine Speed (RPM)", "Vehicle Speed (rad/s)", "Gear"])

# --- MQTT Callback ---
def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        e_speed, v_speed, gear = map(float, payload.split(","))
        timestamps.append(len(timestamps))
        rpms.append(e_speed)
        velocidades.append(v_speed)
        writer.writerow([e_speed, v_speed, int(gear)])
    except ValueError:
        pass  # Ignore invalid data

# --- MQTT Setup ---
client = mqtt.Client()
client.on_message = on_message
client.connect("localhost", 1883)
client.subscribe("tractor/data")
client.loop_start()

# --- Plot setup ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

def animate(i):
    ax1.clear()
    ax2.clear()

    ax1.plot(timestamps, velocidades, label="Velocidad Angular (rad/s)", color="green")
    ax2.plot(timestamps, rpms, label="RPM", color="blue")

    ax1.set_ylabel("Velocidad Angular (rad/s)")
    ax2.set_ylabel("RPM")
    ax2.set_xlabel("Tiempo (s)")
    ax1.set_title("Datos en Tiempo Real")
    ax1.legend()
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

# --- Launch animation ---
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.tight_layout()
plt.show()

# --- Cleanup ---
client.loop_stop()
client.disconnect()
csv_file.close()
