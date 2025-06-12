import tkinter as tk
from tkinter import ttk
import threading
import json
from datetime import datetime

import paho.mqtt.client as mqtt

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# === MQTT Setup ===
broker_address = "localhost"
topic_sub = "tractor/data"
topic_pub = "tractor/control"

rpm_data = []
vel_lineal_data = []
gear_data = []
timestamps = []

# Estado de modo manual/automático
modo_manual = tk.BooleanVar(value=False)
throttle_on = tk.BooleanVar(value=False)
brake_on    = tk.BooleanVar(value=False)

def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm  = data.get("rpm")
        vl   = data.get("spd")
        gear = data.get("gear")
        now  = datetime.now().strftime("%H:%M:%S")
        if rpm is not None and vl is not None and gear is not None:
            rpm_data.append(rpm)
            vel_lineal_data.append(vl)
            gear_data.append(gear)
            timestamps.append(now)
    except Exception as e:
        print("Error al procesar el mensaje:", e)

# Inicializamos cliente MQTT
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def mqtt_loop():
    client.loop_forever()

threading.Thread(target=mqtt_loop, daemon=True).start()

# === Interfaz Tkinter ===
root = tk.Tk()
root.title("Dashboard del Tractor")

# ---- Frame de controles ----
ctrl_frame = ttk.Frame(root, padding=10)
ctrl_frame.pack(side=tk.TOP, fill=tk.X)

# Switch Automático / Manual
modo_chk = ttk.Checkbutton(
    ctrl_frame, text="Modo Manual",
    variable=modo_manual,
    command=lambda: manual_frame.pack_forget() if not modo_manual.get() else manual_frame.pack(fill=tk.X, pady=5)
)
modo_chk.pack(side=tk.LEFT, padx=5)

# Frame de controles manuales (oculto inicialmente)
manual_frame = ttk.Frame(root, padding=10, relief=tk.RIDGE)
# Acelerador
accel_chk = ttk.Checkbutton(
    manual_frame, text="Acelerador",
    variable=throttle_on,
    command=lambda: publish_control()
)
accel_chk.pack(side=tk.LEFT, padx=10)
# Freno
brake_chk = ttk.Checkbutton(
    manual_frame, text="Freno",
    variable=brake_on,
    command=lambda: publish_control()
)
brake_chk.pack(side=tk.LEFT, padx=10)

# ---- Frame de gráficos ----
plots_frame = ttk.Frame(root)
plots_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# Helper para crear un canvas con matplotlib
def create_plot(parent, title, ylabel):
    fig = Figure(figsize=(4,2), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_title(title)
    ax.set_xlabel("Tiempo")
    ax.set_ylabel(ylabel)
    line, = ax.plot([], [], marker='o')
    canvas = FigureCanvasTkAgg(fig, master=parent)
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
    return fig, ax, line, canvas

rpm_fig,  rpm_ax,  rpm_line,  rpm_canvas  = create_plot(plots_frame, "RPM del Motor", "RPM")
vel_fig,  vel_ax,  vel_line,  vel_canvas  = create_plot(plots_frame, "Velocidad Lineal", "km/h")
gear_fig, gear_ax, gear_line, gear_canvas = create_plot(plots_frame, "Marcha", "Gear")

# Publicar control en MQTT
def publish_control():
    if modo_manual.get():
        throttle = 100 if throttle_on.get() else 0
        brake    = 100 if brake_on.get()    else 0
        payload = json.dumps({"throttle": throttle, "brake": brake})
        client.publish(topic_pub, payload)

# Función para actualizar gráficos periódicamente
def update_graphs():
    # Actualizar datos de RPM
    rpm_line.set_data(timestamps, rpm_data)
    rpm_ax.relim(); rpm_ax.autoscale_view()
    rpm_canvas.draw()
    # Velocidad
    vel_line.set_data(timestamps, vel_lineal_data)
    vel_ax.relim(); vel_ax.autoscale_view()
    vel_canvas.draw()
    # Marcha
    gear_line.set_data(timestamps, gear_data)
    gear_ax.relim(); gear_ax.autoscale_view()
    gear_canvas.draw()
    # Reprogramar
    root.after(1000, update_graphs)

# Iniciar bucle de actualización
root.after(1000, update_graphs)

root.mainloop()