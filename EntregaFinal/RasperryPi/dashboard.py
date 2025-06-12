import tkinter as tk
from tkinter import ttk
import threading
import json
from datetime import datetime

import paho.mqtt.client as mqtt

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib import dates as mdates
from matplotlib.animation import FuncAnimation

# === CONFIGURACIÓN MQTT ===
BROKER    = "192.168.137.59"  # Ajusta a la IP de tu broker
TOPIC_SUB = "tractor/data"
TOPIC_PUB = "tractor/control"

# === CONTENEDORES DE DATOS ===
timestamps = []
rpm_data   = []
vel_data   = []
gear_data  = []

# === CALLBACKS MQTT ===
def on_connect(client, userdata, flags, rc, properties=None):
    print("✅ MQTT conectado con código", rc)
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        if all(k in payload for k in ("rpm","spd","gear")):
            now = datetime.now()
            timestamps.append(now)
            rpm_data.append(payload["rpm"])
            vel_data.append(payload["spd"])
            gear_data.append(payload["gear"])
            print(f"🕒 {now.strftime('%H:%M:%S')}  rpm={payload['rpm']} spd={payload['spd']} gear={payload['gear']}")
    except Exception as e:
        print("⚠ Error al procesar MQTT:", e)

# Inicializar cliente MQTT
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(BROKER, 1883, 60)
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

# === INTERFAZ TKINTER ===
root = tk.Tk()
root.title("Dashboard del Tractor")

# Variables de control
manual_mode  = tk.BooleanVar(value=False)
throttle_on  = tk.BooleanVar(value=False)
brake_on     = tk.BooleanVar(value=False)

# — Frame de controles —
ctrl = ttk.Frame(root, padding=8)
ctrl.pack(fill=tk.X)

ttk.Checkbutton(
    ctrl, text="Modo Manual",
    variable=manual_mode,
    command=lambda: (
        manual_frame.pack_forget()
        if not manual_mode.get()
        else manual_frame.pack(fill=tk.X, pady=5)
    )
).pack(side=tk.LEFT, padx=5)

manual_frame = ttk.Frame(root, padding=8, relief=tk.RIDGE)
ttk.Checkbutton(
    manual_frame, text="Acelerador",
    variable=throttle_on,
    command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)
ttk.Checkbutton(
    manual_frame, text="Freno",
    variable=brake_on,
    command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)

# — Figura y Canvas —
fig = Figure(figsize=(8, 6), dpi=100)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
for ax, title in (
    (ax1, "RPM del Motor"),
    (ax2, "Velocidad Lineal (km/h)"),
    (ax3, "Marcha"),
):
    ax.set_title(title)
    ax.set_ylabel("")  # Se asigna en animate()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.grid(True)
fig.autofmt_xdate()

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# — Función de publicación MQTT —
def publish_control():
    if manual_mode.get():
        msg = {
            "throttle": 100 if throttle_on.get() else 0,
            "brake":    100 if brake_on.get()    else 0
        }
        mqtt_client.publish(TOPIC_PUB, json.dumps(msg))
        print("📤 Publicado control:", msg)

# — Función de animación de Matplotlib —
def animate(frame):
    if not timestamps:
        return
    # convierte timestamps a números de Matplotlib
    x = mdates.date2num(timestamps)

    # limpiar axes
    ax1.clear(); ax2.clear(); ax3.clear()
    # plot
    ax1.plot_date(x, rpm_data, '-o')
    ax2.plot_date(x, vel_data, '-o')
    ax3.plot_date(x, gear_data, '-o')

    # Estilo y límites
    for ax, ylabel in ((ax1,"RPM"), (ax2,"km/h"), (ax3,"Gear")):
        ax.set_ylabel(ylabel)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.relim(); ax.autoscale_view(True, tight=True)
    fig.autofmt_xdate()

# — Inicializar animación cada 1s —
ani = FuncAnimation(fig, animate, interval=1000)

root.mainloop()