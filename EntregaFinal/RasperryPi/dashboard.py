import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt
import json
import csv
import os
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# MQTT Configuration
broker_address = "192.168.137.59"
topic_pub = "tractor/inputs"
topic_sub = "tractor/data"

# Data containers
time_data = []
rpm_data = []
vel_lineal_data = []
gear_data = []

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Conectado con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())

        rpm = data["rpm"]
        vel_lineal = data["velocity"]
        gear = data["gear"]

        timestamp = time.time()  # timestamp en segundos

        time_data.append(timestamp)
        rpm_data.append(rpm)
        vel_lineal_data.append(vel_lineal)
        gear_data.append(gear)

        # Guarda en CSV
        csv_path = os.path.join(os.getcwd(), "datos_tractor.csv")
        write_header = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(["Timestamp", "RPM", "Velocidad Lineal (m/s)", "Gear"])
            writer.writerow([timestamp, rpm, vel_lineal, gear])

    except Exception as e:
        print("Error procesando mensaje:", e)

def send_data():
    try:
        vel_angular  = float(entry_vel_angular.get())
        trans_ratio  = float(entry_trans_ratio.get())
        wheel_radius = float(entry_wheel_radius.get())
        payload = {
            "velocidad_angular":    vel_angular,
            "relacion_transmision": trans_ratio,
            "radio_rueda":          wheel_radius
        }
        client.publish(topic_pub, json.dumps(payload))
        print("Datos enviados:", payload)
    except ValueError:
        messagebox.showerror("Error", "Ingresa valores numéricos válidos")

# Setup MQTT callbacks
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.loop_start()

# Tkinter GUI Setup
root = tk.Tk()
root.title("Control de Tractor")

tk.Label(root, text="Velocidad Angular (rad/s)").grid(row=0, column=0)
entry_vel_angular = tk.Entry(root)
entry_vel_angular.grid(row=0, column=1)

tk.Label(root, text="Relación Transmisión").grid(row=1, column=0)
entry_trans_ratio = tk.Entry(root)
entry_trans_ratio.grid(row=1, column=1)

tk.Label(root, text="Radio de Rueda (m)").grid(row=2, column=0)
entry_wheel_radius = tk.Entry(root)
entry_wheel_radius.grid(row=2, column=1)

tk.Button(root, text="Enviar", command=send_data).grid(row=3, column=0, columnspan=2, pady=10)

# Matplotlib Figure
fig = Figure(figsize=(6, 6))
ax_rpm = fig.add_subplot(311)
ax_vel = fig.add_subplot(312)
ax_gear = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)

def update_plot():
    if len(time_data) > 0:
        # Convierto timestamps a tiempo relativo para mejor visualización
        t0 = time_data[0]
        t_rel = [t - t0 for t in time_data]

        ax_rpm.clear()
        ax_vel.clear()
        ax_gear.clear()

        ax_rpm.plot(t_rel, rpm_data, label="RPM", color='blue')
        ax_rpm.set_ylabel("RPM")
        ax_rpm.legend()
        ax_rpm.grid(True)

        ax_vel.plot(t_rel, vel_lineal_data, label="Vel. Lineal (m/s)", color='green')
        ax_vel.set_ylabel("Velocidad")
        ax_vel.legend()
        ax_vel.grid(True)

        ax_gear.plot(t_rel, gear_data, label="Marcha", color='red', marker='o')
        ax_gear.set_ylabel("Marcha")
        ax_gear.legend()
        ax_gear.grid(True)

        ax_gear.set_xlabel("Tiempo (s)")

        canvas.draw()

    # Llama a esta función cada 500 ms para actualizar la gráfica
    root.after(500, update_plot)

update_plot()

root.protocol("WM_DELETE_WINDOW", lambda: (client.loop_stop(), client.disconnect(), root.destroy()))

root.mainloop()
