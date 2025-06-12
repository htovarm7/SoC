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

# Variable para modo de control: True = manual (dashboard), False = automático (potenciómetro)
manual_mode = tk.BooleanVar(value=True)

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

        # Si está en modo automático, actualizar entradas con datos recibidos
        if not manual_mode.get():
            # Actualiza entradas de la GUI (esto refleja los valores recibidos)
            entry_vel_angular.delete(0, tk.END)
            entry_vel_angular.insert(0, str(round(vel_lineal, 3)))  # ejemplo: usa velocidad lineal para demo
            entry_trans_ratio.delete(0, tk.END)
            entry_trans_ratio.insert(0, str(gear))  # ejemplo: usa gear para demo
            entry_wheel_radius.delete(0, tk.END)
            entry_wheel_radius.insert(0, "0")  # o algún valor fijo / calculado

    except Exception as e:
        print("Error procesando mensaje:", e)

def send_data():
    if not manual_mode.get():
        messagebox.showinfo("Modo Automático", "Actualmente en modo automático, no se pueden enviar datos manualmente.")
        return

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

def toggle_mode():
    if manual_mode.get():
        send_button.config(state="normal")
        # Opcional: limpiar o permitir editar entradas manualmente
        entry_vel_angular.config(state="normal")
        entry_trans_ratio.config(state="normal")
        entry_wheel_radius.config(state="normal")
    else:
        send_button.config(state="disabled")
        # En modo automático, bloquea edición para reflejar datos recibidos
        entry_vel_angular.config(state="readonly")
        entry_trans_ratio.config(state="readonly")
        entry_wheel_radius.config(state="readonly")

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

send_button = tk.Button(root, text="Enviar", command=send_data)
send_button.grid(row=3, column=0, columnspan=2, pady=10)

# Switch para modo manual/automático
mode_switch = tk.Checkbutton(root, text="Modo Manual (Dashboard) / Automático (Potenciómetro)",
                             variable=manual_mode, command=toggle_mode)
mode_switch.grid(row=5, column=0, columnspan=2, pady=5)

# Matplotlib Figure embedded in Tkinter
fig = Figure(figsize=(6, 6))
ax_rpm = fig.add_subplot(311)
ax_vel = fig.add_subplot(312)
ax_gear = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, column=0, columnspan=2)

def update_plot():
    if len(time_data) == 0:
        root.after(100, update_plot)
        return

    # Recorta para que todas las listas tengan la misma longitud
    min_len = min(len(time_data), len(rpm_data), len(vel_lineal_data), len(gear_data))
    if min_len == 0:
        root.after(100, update_plot)
        return

    t_rel = [t - time_data[0] for t in time_data[:min_len]]
    rpm_plot = rpm_data[:min_len]
    vel_plot = vel_lineal_data[:min_len]
    gear_plot = gear_data[:min_len]

    # Limpia e inserta las gráficas
    ax_rpm.clear()
    ax_vel.clear()
    ax_gear.clear()

    ax_rpm.plot(t_rel, rpm_plot, label="RPM", color='blue')
    ax_rpm.set_ylabel("RPM")
    ax_rpm.legend()
    
    ax_vel.plot(t_rel, vel_plot, label="Vel. Lineal (m/s)", color='green')
    ax_vel.set_ylabel("Velocidad")
    ax_vel.legend()
    
    ax_gear.plot(t_rel, gear_plot, label="Marcha", color='red', marker='o')
    ax_gear.set_ylabel("Marcha")
    ax_gear.legend()

    fig.tight_layout()
    canvas.draw()

    # Llama esta función cada 100 ms para actualizar la gráfica
    root.after(100, update_plot)

# Inicializa estado del switch para configurar UI
toggle_mode()

# Arranca la actualización periódica del gráfico
root.after(100, update_plot)

# Cierre limpio
def on_closing():
    client.loop_stop()
    client.disconnect()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
