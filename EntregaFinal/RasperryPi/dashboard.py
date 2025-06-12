import tkinter as tk
from tkinter import messagebox
import paho.mqtt.client as mqtt
import json
import matplotlib.pyplot as plt
import csv
import os

# MQTT Configuration
broker_address = "192.168.137.59"
topic_pub = "tractor/inputs"
topic_sub = "tractor/data"  # debe coincidir con la ESP32

# Data containers
rpm_data = []
vel_lineal_data = []
gear_data = []

# MQTT Client Setup
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Conectado con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):

    print("Mensaje recibido:", msg.payload.decode())

    try:

        data = json.loads(msg.payload.decode())

        rpm = data["rpm"]

        vel_lineal = data["velocity"]

        gear = data["gear"]



        rpm_data.append(rpm)

        vel_lineal_data.append(vel_lineal)

        gear_data.append(gear)



        # Construye la ruta al CSV usando _file_

        csv_path = os.path.join(

            os.path.dirname(os.path.abspath(__file__)),

            "datos_tractor.csv"

        )

        write_header = not os.path.exists(csv_path)



        # Abre y escribe usando 'csvfile', nunca 'file' ni 'file'

        with open(csv_path, "a", newline="") as csvfile:

            writer = csv.writer(csvfile)

            if write_header:

                writer.writerow(["RPM", "Velocidad Lineal (m/s)", "Gear"])

            writer.writerow([rpm, vel_lineal, gear])



        plot_data()

    except Exception as e:

        print("Error procesando mensaje:", e)

def plot_data():
    plt.clf()
    # Gráfica RPM
    plt.subplot(3, 1, 1)
    plt.plot(rpm_data, label="RPM")
    plt.ylabel("RPM")
    plt.legend()

    # Gráfica Velocidad lineal
    plt.subplot(3, 1, 2)
    plt.plot(vel_lineal_data, label="Vel. Lineal (m/s)")
    plt.ylabel("Velocidad")
    plt.legend()

    # Gráfica Marcha
    plt.subplot(3, 1, 3)
    plt.plot(gear_data, label="Marcha", marker='o')
    plt.ylabel("Marcha")
    plt.legend()

    plt.tight_layout()
    plt.pause(0.1)  # refresca la ventana

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

# Asignar callbacks ANTES de conectar
client.on_connect = on_connect
client.on_message = on_message
# Inicia loop MQTT en background
client.connect(broker_address, 1883, 60)
client.loop_start()

# GUI Setup
root = tk.Tk()
root.title("Control de Tractor")

tk.Label(root, text="Velocidad Angular (rad/s)").grid(row=0, column=0)
entry_vel_angular = tk.Entry(root); entry_vel_angular.grid(row=0, column=1)

tk.Label(root, text="Relación Transmisión").grid(row=1, column=0)
entry_trans_ratio = tk.Entry(root); entry_trans_ratio.grid(row=1, column=1)

tk.Label(root, text="Radio de Rueda (m)").grid(row=2, column=0)
entry_wheel_radius = tk.Entry(root); entry_wheel_radius.grid(row=2, column=1)

tk.Button(root, text="Enviar", command=send_data).grid(row=3, column=0, columnspan=2, pady=10)

# Configura matplotlib en modo interactivo
plt.ion()
plt.show()

root.mainloop()

# Al cerrar la GUI, detenemos el loop MQTT
client.loop_stop()
client.disconnect()