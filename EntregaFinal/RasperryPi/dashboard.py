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
broker_address = "192.168.137.59"  # Dirección IP del broker MQTT
topic_pub = "tractor/inputs"       # Tópico al que se envían comandos desde Python
topic_sub = "tractor/data"         # Tópico desde donde se reciben datos de la ESP32

# Contenedores de datos para gráficas
time_data = []
rpm_data = []
vel_lineal_data = []
gear_data = []

# Cliente MQTT
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data["rpm"]
        vel_lineal = data["velocity"]
        gear = data["gear"]

        timestamp = time.time()

        # Agrega datos
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

        # En modo automático: llenar entradas GUI con datos recibidos
        if not manual_mode.get():
            entry_vel_angular.config(state="normal")
            entry_trans_ratio.config(state="normal")
            entry_wheel_radius.config(state="normal")

            entry_vel_angular.delete(0, tk.END)
            entry_vel_angular.insert(0, str(round(vel_lineal, 2)))  # opcional
            entry_trans_ratio.delete(0, tk.END)
            entry_trans_ratio.insert(0, str(gear))
            entry_wheel_radius.delete(0, tk.END)
            entry_wheel_radius.insert(0, "0")

            entry_vel_angular.config(state="readonly")
            entry_trans_ratio.config(state="readonly")
            entry_wheel_radius.config(state="readonly")

    except Exception as e:
        print("Error procesando mensaje MQTT:", e)

def send_brake():
    if not manual_mode.get():
        messagebox.showinfo("Modo Automático", "No se puede activar freno en modo automático.")
        return

    payload = {"freno": True}
    client.publish(topic_pub, json.dumps(payload))
    print("Se envió freno:", payload)

def send_data():
    if not manual_mode.get():
        messagebox.showinfo("Modo Automático", "No se pueden enviar datos manualmente.")
        return

    try:
        vel_angular  = float(entry_vel_angular.get())
        trans_ratio  = float(entry_trans_ratio.get())
        wheel_radius = float(entry_wheel_radius.get())
        payload = {
            "velocidad_angular": vel_angular,
            "relacion_transmision": trans_ratio,
            "radio_rueda": wheel_radius
        }
        client.publish(topic_pub, json.dumps(payload))
        print("Se enviaron datos:", payload)
    except ValueError:
        messagebox.showerror("Error", "Por favor, introduce valores numéricos válidos.")

def toggle_mode():
    if manual_mode.get():
        send_button.config(state="normal")
        entry_vel_angular.config(state="normal")
        entry_trans_ratio.config(state="normal")
        entry_wheel_radius.config(state="normal")
    else:
        send_button.config(state="disabled")
        entry_vel_angular.config(state="readonly")
        entry_trans_ratio.config(state="readonly")
        entry_wheel_radius.config(state="readonly")

# Configura cliente MQTT
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.loop_start()

# Interfaz Gráfica
root = tk.Tk()
root.title("Dashboard de Control de Tractor")

manual_mode = tk.BooleanVar(value=True)

tk.Label(root, text="Velocidad Angular (rad/s)").grid(row=0, column=0)
entry_vel_angular = tk.Entry(root)
entry_vel_angular.grid(row=0, column=1)

tk.Label(root, text="Relación Transmisión").grid(row=1, column=0)
entry_trans_ratio = tk.Entry(root)
entry_trans_ratio.grid(row=1, column=1)

tk.Label(root, text="Radio de Rueda (m)").grid(row=2, column=0)
entry_wheel_radius = tk.Entry(root)
entry_wheel_radius.grid(row=2, column=1)

send_button = tk.Button(root, text="Enviar Datos", command=send_data)
send_button.grid(row=3, column=0, columnspan=2, pady=10)

brake_button = tk.Button(root, text="Activar Freno", command=send_brake)
brake_button.grid(row=4, column=0, columnspan=2, pady=5)

mode_switch = tk.Checkbutton(root, text="Modo Manual / Automático",
                             variable=manual_mode, command=toggle_mode)
mode_switch.grid(row=5, column=0, columnspan=2, pady=5)

# Gráficas
fig = Figure(figsize=(6, 6))
ax_rpm = fig.add_subplot(311)
ax_vel = fig.add_subplot(312)
ax_gear = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=6, column=0, columnspan=2)

def update_plot():
    if len(time_data) == 0:
        root.after(100, update_plot)
        return

    min_len = min(len(time_data), len(rpm_data), len(vel_lineal_data), len(gear_data))
    t_rel = [t - time_data[0] for t in time_data[:min_len]]

    ax_rpm.clear()
    ax_vel.clear()
    ax_gear.clear()

    ax_rpm.plot(t_rel, rpm_data[:min_len], label="RPM", color='blue')
    ax_rpm.set_ylabel("RPM")
    ax_rpm.legend()

    ax_vel.plot(t_rel, vel_lineal_data[:min_len], label="Velocidad (m/s)", color='green')
    ax_vel.set_ylabel("Velocidad")
    ax_vel.legend()

    ax_gear.plot(t_rel, gear_data[:min_len], label="Marcha", color='red', marker='o')
    ax_gear.set_ylabel("Marcha")
    ax_gear.legend()

    fig.tight_layout()
    canvas.draw()
    root.after(100, update_plot)

toggle_mode()
root.after(100, update_plot)

def on_closing():
    client.loop_stop()
    client.disconnect()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
