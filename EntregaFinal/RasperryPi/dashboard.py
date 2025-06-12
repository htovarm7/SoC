import tkinter as tk
from tkinter import messagebox, ttk
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
topic_control = "tractor/control"   # para freno/acelerar

# Data containers
time_data = []
rpm_data = []
vel_lineal_data = []
gear_data = []

# === MQTT Client Setup ===
client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print("Conectado con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm        = data["rpm"]
        vel_lineal = data["velocity"]
        gear       = data["gear"]
        timestamp  = time.time()

        time_data.append(timestamp)
        rpm_data.append(rpm)
        vel_lineal_data.append(vel_lineal)
        gear_data.append(gear)

        # Guarda en CSV
        csv_path     = os.path.join(os.getcwd(), "datos_tractor.csv")
        write_header = not os.path.exists(csv_path)
        with open(csv_path, "a", newline="") as csvfile:
            writer = csv.writer(csvfile)
            if write_header:
                writer.writerow(["Timestamp", "RPM", "Velocidad Lineal (m/s)", "Gear"])
            writer.writerow([timestamp, rpm, vel_lineal, gear])

        # Si está en modo automático, reflejar datos en los entries
        if not manual_mode.get():
            for entry, val in [
                (entry_vel_angular,  round(vel_lineal,3)),
                (entry_trans_ratio,  gear),
                (entry_wheel_radius, 0)
            ]:
                entry.config(state="normal")
                entry.delete(0, tk.END)
                entry.insert(0, str(val))
                entry.config(state="readonly")

    except Exception as e:
        print("Error procesando mensaje:", e)

client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.loop_start()

# === Tkinter GUI Setup ===
root = tk.Tk()
root.title("Control de Tractor")

# Variables para modo y manual controls
manual_mode  = tk.BooleanVar(value=True)   # True = permite envío manual
throttle_on  = tk.BooleanVar(value=False)
brake_on     = tk.BooleanVar(value=False)

# Entradas de datos
tk.Label(root, text="Velocidad Angular (rad/s)").grid(row=0, column=0)
entry_vel_angular = tk.Entry(root)
entry_vel_angular.grid(row=0, column=1)

tk.Label(root, text="Relación Transmisión").grid(row=1, column=0)
entry_trans_ratio = tk.Entry(root)
entry_trans_ratio.grid(row=1, column=1)

tk.Label(root, text="Radio de Rueda (m)").grid(row=2, column=0)
entry_wheel_radius = tk.Entry(root)
entry_wheel_radius.grid(row=2, column=1)

# Botón enviar (solo en modo manual para potenciómetro)
send_button = tk.Button(root, text="Enviar", command=lambda: send_data())
send_button.grid(row=3, column=0, columnspan=2, pady=10)

# Switch modo Manual/Automático
mode_switch = tk.Checkbutton(
    root, text="Modo Manual / Automático",
    variable=manual_mode, command=lambda: toggle_mode()
)
mode_switch.grid(row=4, column=0, columnspan=2, pady=5)

# Frame para controles de freno/acelerar (solo en modo manual)
manual_frame = ttk.Frame(root, padding=5, relief=tk.RIDGE)
ttk.Checkbutton(
    manual_frame, text="Acelerador",
    variable=throttle_on, command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)
ttk.Checkbutton(
    manual_frame, text="Freno",
    variable=brake_on, command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)

# Matplotlib Figure embedded in Tkinter
fig   = Figure(figsize=(6, 6))
ax_r  = fig.add_subplot(311)
ax_v  = fig.add_subplot(312)
ax_g  = fig.add_subplot(313)
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=5, column=0, columnspan=2)

# Función para enviar datos de los entries
def send_data():
    if not manual_mode.get():
        messagebox.showinfo("Modo Automático", "No se puede enviar manualmente en Modo Automático.")
        return
    try:
        vel_ang  = float(entry_vel_angular.get())
        trans_r  = float(entry_trans_ratio.get())
        wheel_r  = float(entry_wheel_radius.get())
        payload = {
            "velocidad_angular":    vel_ang,
            "relacion_transmision": trans_r,
            "radio_rueda":          wheel_r
        }
        client.publish(topic_pub, json.dumps(payload))
        print("Datos enviados:", payload)
    except ValueError:
        messagebox.showerror("Error", "Ingresa valores numéricos válidos.")

# Función para publicar freno/acelerar
def publish_control():
    if manual_mode.get():
        msg = {
            "throttle": 100 if throttle_on.get() else 0,
            "brake":    100 if brake_on.get()    else 0
        }
        client.publish(topic_control, json.dumps(msg))
        print("📤 Control publicado:", msg)

# Ajusta widgets según modo
def toggle_mode():
    if manual_mode.get():
        send_button.config(state="normal")
        entry_vel_angular.config(state="normal")
        entry_trans_ratio.config(state="normal")
        entry_wheel_radius.config(state="normal")
        manual_frame.grid(row=6, column=0, columnspan=2, pady=5)
    else:
        send_button.config(state="disabled")
        for e in (entry_vel_angular, entry_trans_ratio, entry_wheel_radius):
            e.config(state="readonly")
        manual_frame.grid_forget()

# Función periódica para actualizar el plot
def update_plot():
    if not time_data:
        root.after(100, update_plot)
        return

    n = min(len(time_data), len(rpm_data), len(vel_lineal_data), len(gear_data))
    t_rel    = [t - time_data[0] for t in time_data[:n]]
    rpm_p    = rpm_data[:n]
    vel_p    = vel_lineal_data[:n]
    gear_p   = gear_data[:n]

    ax_r.clear(); ax_v.clear(); ax_g.clear()
    ax_r.plot(t_rel, rpm_p, label="RPM", color='blue'); ax_r.legend()
    ax_v.plot(t_rel, vel_p, label="Vel. Lineal (m/s)", color='green'); ax_v.legend()
    ax_g.plot(t_rel, gear_p, label="Marcha", color='red', marker='o'); ax_g.legend()
    fig.tight_layout()
    canvas.draw()

    root.after(100, update_plot)

# Inicializa estado y ciclo de actualización
toggle_mode()
root.after(100, update_plot)

def on_closing():
    client.loop_stop()
    client.disconnect()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()