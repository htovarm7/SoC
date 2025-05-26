"""
 * @file graphs.py
 * @date 17/5/2025
 * @author Hector Tovar
 * 
 * @brief This script simulates and visualizes real-time tractor telemetry data (speed, acceleration, gear)
 * using random values and matplotlib animation. No MQTT or GUI framework is used.
"""

import csv
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- CSV Setup ---
csv_file = open("tractor_data.csv", "w", newline='')
writer = csv.writer(csv_file)
writer.writerow(["Speed (m/s)", "Acceleration (m/s^2)", "Gear"])

# --- Data Lists ---
timestamps = []
speeds = []
accelerations = []
gears = []

# --- Generate Random Data Function ---
def generar_dato():
    t = len(timestamps)
    velocidad = random.uniform(0, 30)  # velocidad en m/s
    aceleracion = random.uniform(-3, 3)  # aceleración en m/s^2
    marcha = random.randint(1, 6)  # marcha del tractor (1 a 6)

    timestamps.append(t)
    speeds.append(velocidad)
    accelerations.append(aceleracion)
    gears.append(marcha)

    writer.writerow([velocidad, aceleracion, marcha])

# --- Matplotlib Setup ---
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

def animate(i):
    generar_dato()

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

    ax1.set_title("Simulación de Telemetría en Tiempo Real")
    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    plt.setp(ax3.get_xticklabels(), rotation=45, ha="right")

# --- Start Animation ---
ani = animation.FuncAnimation(fig, animate, interval=1000)  # 1 segundo de intervalo
plt.tight_layout()
plt.show()

# --- Cleanup ---
csv_file.close()
