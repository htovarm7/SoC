import random
import math
import csv
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from datetime import datetime

# --- CSV File ---
CSV_FILENAME = "datos_tractor.csv"
CSV_HEADER = ["timestamp", "velocidad_angular", "radio_rueda", "relacion_transmision", "rpm"]

# --- Initialization of lists for plotting ---
timestamps = []
velocidades = []
rpms = []

# --- Constantes ---
RADIO_RUEDA = 0.5  # m, constante
RELACION_TRANSMISION = 10  # constante

# --- Create CSV file if it does not exist ---
with open(CSV_FILENAME, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    if csvfile.tell() == 0:
        writer.writerow(CSV_HEADER)

# --- Function to calculate RPM ---
def calcular_rpm(velocidad_angular, radio_rueda, relacion_transmision):
    return (velocidad_angular * 60) / (2 * math.pi * radio_rueda * relacion_transmision)

# --- Function to generate and save data ---
def generar_dato():
    velocidad_angular = random.uniform(5, 10)   # rad/s
    rpm = calcular_rpm(velocidad_angular, RADIO_RUEDA, RELACION_TRANSMISION)
    timestamp = datetime.now().strftime("%H:%M:%S")

    # Save to lists
    timestamps.append(timestamp)
    velocidades.append(velocidad_angular)
    rpms.append(rpm)

    # Limit to the last 50 points
    if len(timestamps) > 50:
        timestamps.pop(0)
        velocidades.pop(0)
        rpms.pop(0)

    # Save to CSV
    with open(CSV_FILENAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, velocidad_angular, RADIO_RUEDA, RELACION_TRANSMISION, rpm])

# --- Animation function ---
def animate(i):
    generar_dato()

    ax1.clear()
    ax2.clear()
    ax1.plot(timestamps, velocidades, label="Velocidad Angular (rad/s)", color="green")
    ax2.plot(timestamps, rpms, label="RPM", color="blue")

    ax1.set_ylabel("Velocidad Angular (rad/s)")
    ax2.set_ylabel("RPM")
    ax2.set_xlabel("Tiempo")
    ax1.set_title("Simulación en tiempo real")
    ax1.legend()
    ax2.legend()
    ax1.grid(True)
    ax2.grid(True)
    plt.setp(ax1.get_xticklabels(), rotation=45, ha="right")
    plt.setp(ax2.get_xticklabels(), rotation=45, ha="right")

# --- Configure plot ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
ani = animation.FuncAnimation(fig, animate, interval=1000)

plt.tight_layout()
plt.show()
