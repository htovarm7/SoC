import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import csv
import os
import threading

# MQTT Configuration
broker_address ="192.168.137.59"
topic_pub = "tractor/inputs"
topic_sub = "tractor/data"  # Cambiado para que coincida con la ESP32

# Data containers
rpm_data = []
vel_lineal_data = []
gear_data = []

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Conectado con código: " + str(rc))
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    print("Mensaje recibido:", msg.payload.decode())
    try:
        data = json.loads(msg.payload.decode())
        rpm = data["rpm"]
        vel_lineal = data["velocity"]  # Antes: data["vel_lineal"]
        gear = data["gear"]
        gear_data.append(gear)


        rpm_data.append(rpm)
        vel_lineal_data.append(vel_lineal)

        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_tractor.csv")
        write_header = not os.path.exists(csv_path)

        with open(csv_path, "a", newline="") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["RPM", "Velocidad Lineal (m/s)", "Gear"])
            writer.writerow([rpm, vel_lineal, data["gear"]])  # También guardamos gear

        plot_data()
    except Exception as e:
        print("Error procesando mensaje:", e)

def plot_data():
    plt.clf()

    plt.subplot(3, 1, 1)
    plt.plot(rpm_data, label="RPM", color="blue")
    plt.xlabel("Mediciones")
    plt.ylabel("RPM")
    plt.legend()

    plt.subplot(3, 1, 2)
    plt.plot(vel_lineal_data, label="Vel. Lineal (m/s)", color="green")
    plt.xlabel("Mediciones")
    plt.ylabel("Vel. Lineal")
    plt.legend()

    plt.subplot(3, 1, 3)
    plt.plot(gear_data, label="Marcha", color="red", marker='o')
    plt.xlabel("Mediciones")
    plt.ylabel("Marcha")
    plt.legend()

    plt.tight_layout()
    plt.pause(0.1)

def send_data():
    try:
        vel_angular = float(entry_vel_angular.get())
        trans_ratio = float(entry_trans_ratio.get())
        wheel_radius = float(entry_wheel_radius.get())

        data = {
            "velocidad_angular": vel_angular,
            "relacion_transmision": trans_ratio,
            "radio_rueda": wheel_radius
        }
        client.publish(topic_pub, json.dumps(data))
        print(f"Datos enviados: {data}")
    except ValueError:
        messagebox.showerror("Error", "Por favor ingresa valores numéricos válidos")

def start_mqtt():
    client.loop_forever()

# GUI Setup
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

send_button = tk.Button(root, text="Enviar", command=send_data)
send_button.grid(row=3, column=0, columnspan=2, pady=10)

# Thread for MQTT
mqtt_thread = threading.Thread(target=start_mqtt)
mqtt_thread.daemon = True
mqtt_thread.start()

# Setup matplotlib
plt.ion()
plt.show()

root.mainloop()

client.disconnect()
