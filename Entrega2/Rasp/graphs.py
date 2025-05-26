"""
 * @file graphs_mqtt.py
 * @date 25/5/2025
 * @author Hector Tovar
 * 
 * @brief This script receives tractor telemetry data (speed, acceleration, gear)
 * from MQTT and visualizes it in real-time using matplotlib.
"""

import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import paho.mqtt.client as mqtt
import json
from collections import deque

# --- MQTT Configuration ---
MQTT_BROKER = "localhost"  # o la IP de la Raspberry Pi
MQTT_PORT = 1883
MQTT_TOPIC = "tractor/data"

# --- CSV Setup ---
csv_file = open("tractor_data.csv", "w", newline='')
writer = csv.writer(csv_file)
writer.writerow(["Speed (m/s)", "Acceleration (m/s^2)", "Gear"])

# --- Data Lists (Fixed Length with deque) ---
MAX_POINTS = 60  # mostrar 60 segundos de datos
timestamps = deque(maxlen=MAX_POINTS)
speeds = deque(maxlen=MAX_POINTS)
accelerations = deque(maxlen=MAX_POINTS)
gears = deque(maxlen=MAX_POINTS)

current_time = 0

# --- MQTT Callback ---
def on_connect(client, userdata, flags, rc):
    print(f"Conectado al broker MQTT con código {rc}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    global current_time
    try:
        payload = json.loads(msg.payload.decode())
        velocidad = float(payload["speed"])
        aceleracion = float(payload["acceleration"])
        marcha = int(payload["gear"])

        timestamps.append(current_time)
        speeds.append(velocidad)
        accelerations.append(aceleracion)
        gears.append(marcha)

        writer.writerow([velocidad, aceleracion, marcha])
        current_time += 1
    except Exception as e:
        print("Error al procesar mensaje:", e)

# --- MQTT Client Setup ---
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

# --- Matplotlib Setup ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

def animate(i):
    ax1.clear()
    ax2.clear()
    ax3.clear()

    ax1.plot(timestamps, speeds, label="Velocidad (m/s)", color="green")
    ax2.plot(timestamps, accelerations, label="Aceleración (m/s²)", color="orange")
    ax3.step(timestamps, gears, label="Marcha", color="blue", where="post")

    ax1.set_ylabel("Velocidad (m/s)")
    ax2.set_ylabel("Aceleración (m/s²)")
    ax3.set_ylabel("Marcha")
    ax3.set_xlabel("Tiempo (s)")

    ax1.legend()
    ax2.legend()
    ax3.legend()

    ax1.set_title("Telemetría del Tractor en Tiempo Real (MQTT)")
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")

# --- Start Animation ---
ani = animation.FuncAnimation(fig, animate, interval=1000)
plt.tight_layout()
plt.show()

# --- Cleanup ---
client.loop_stop()
client.disconnect()
csv_file.close()

