import tkinter as tk
from tkinter import ttk
import threading
import json
from datetime import datetime

import paho.mqtt.client as mqtt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import dates as mdates

# === MQTT Setup ===
broker_address = "192.168.137.59"  # ← Cambiado a la IP de tu broker ESP32
topic_sub      = "tractor/data"
topic_pub      = "tractor/control"

rpm_data         = []
vel_lineal_data  = []
gear_data        = []
timestamps       = []

# === INTERFAZ TKINTER ===
root = tk.Tk()
root.title("Dashboard del Tractor")

modo_manual = tk.BooleanVar(value=False)
throttle_on = tk.BooleanVar(value=False)
brake_on    = tk.BooleanVar(value=False)

# ---- Controles ----
ctrl_frame = ttk.Frame(root, padding=10)
ctrl_frame.pack(fill=tk.X)
ttk.Checkbutton(
    ctrl_frame, text="Modo Manual",
    variable=modo_manual,
    command=lambda: (
        manual_frame.pack_forget()
        if not modo_manual.get()
        else manual_frame.pack(fill=tk.X, pady=5)
    )
).pack(side=tk.LEFT, padx=5)

manual_frame = ttk.Frame(root, padding=10, relief=tk.RIDGE)
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

# ---- Gráficos ----
plots_frame = ttk.Frame(root)
plots_frame.pack(fill=tk.BOTH, expand=True)

def create_plot(parent, title, ylabel):
    fig = Figure(figsize=(5,3), dpi=100)
    ax  = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel("Tiempo")
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    fig.autofmt_xdate()
    line, = ax.plot([], [], marker='o')
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    return ax, line, canvas

rpm_ax,  rpm_line,  rpm_canvas  = create_plot(plots_frame, "RPM del Motor",    "RPM")
vel_ax,  vel_line,  vel_canvas  = create_plot(plots_frame, "Velocidad Lineal","km/h")
gear_ax, gear_line, gear_canvas = create_plot(plots_frame, "Marcha",           "Gear")

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc, properties=None):
    print(f"✅ Conectado al broker MQTT [{broker_address}] con código: {rc}")
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        if all(k in data for k in ("rpm","spd","gear")):
            now = datetime.now()
            rpm_data.append(data["rpm"])
            vel_lineal_data.append(data["spd"])
            gear_data.append(data["gear"])
            timestamps.append(now)
            print(f"🕒 {now.strftime('%H:%M:%S')} → rpm={data['rpm']}, spd={data['spd']}, gear={data['gear']}")
    except Exception as e:
        print("⚠ Error on_message:", e)

client = mqtt.Client(protocol=mqtt.MQTTv311)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def mqtt_loop():
    client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

def publish_control():
    if modo_manual.get():
        payload = json.dumps({
            "throttle": 100 if throttle_on.get() else 0,
            "brake":    100 if brake_on.get()    else 0
        })
        client.publish(topic_pub, payload)
        print("📤 Publicado control:", payload)

def update_graphs():
    print(f"🔄 update_graphs llamado. Puntos recibidos: {len(timestamps)}")
    if timestamps:
        x = mdates.date2num(timestamps)

        # RPM
        rpm_line.set_data(x, rpm_data)
        rpm_ax.set_xlim(x[0], x[-1])
        rpm_ax.relim(); rpm_ax.autoscale_view(True, tight=True)
        rpm_canvas.draw()

        # Velocidad
        vel_line.set_data(x, vel_lineal_data)
        vel_ax.set_xlim(x[0], x[-1])
        vel_ax.relim(); vel_ax.autoscale_view(True, tight=True)
        vel_canvas.draw()

        # Marcha
        gear_line.set_data(x, gear_data)
        gear_ax.set_xlim(x[0], x[-1])
        gear_ax.relim(); gear_ax.autoscale_view(True, tight=True)
        gear_canvas.draw()

    root.after(1000, update_graphs)

root.after(1000, update_graphs)
root.mainloop()