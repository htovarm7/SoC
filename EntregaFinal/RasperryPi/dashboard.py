import tkinter as tk
from tkinter import ttk
from tkinter import BooleanVar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import paho.mqtt.client as mqtt
import json
from datetime import datetime
import threading

# === Variables globales para datos ===
rpm_data = []
vel_lineal_data = []
gear_data = []
timestamps = []

modo_manual = BooleanVar(value=False)
acelerador_on = BooleanVar(value=False)
freno_on = BooleanVar(value=False)

broker_address = "localhost"
topic_sub = "tractor/data"
topic_pub = "tractor/control"

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    print("Conectado al broker MQTT con código:", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data.get("rpm")
        vl = data.get("spd")
        gear = data.get("gear")
        now = datetime.now().strftime("%H:%M:%S")

        if rpm is not None and vl is not None and gear is not None:
            rpm_data.append(rpm)
            vel_lineal_data.append(vl)
            gear_data.append(gear)
            timestamps.append(now)
            # Limitar tamaño de listas para que no crezcan ilimitadamente
            max_len = 50
            if len(rpm_data) > max_len:
                rpm_data.pop(0)
                vel_lineal_data.pop(0)
                gear_data.pop(0)
                timestamps.pop(0)
    except Exception as e:
        print("Error al procesar mensaje MQTT:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop, daemon=True)
mqtt_thread.start()

# === Funciones para publicar control ===
def publicar_control():
    if modo_manual.get():
        throttle = 100 if acelerador_on.get() else 0
        brake = 100 if freno_on.get() else 0
        payload = json.dumps({"throttle": throttle, "brake": brake})
        client.publish(topic_pub, payload)

# === GUI con Tkinter ===
class TractorDashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Dashboard del Tractor")

        # Toggle modo manual/automático
        self.modo_switch = ttk.Checkbutton(self, text="Modo Manual", variable=modo_manual, command=self.toggle_manual)
        self.modo_switch.pack(pady=5)

        # Frame controles manuales (acelerador, freno)
        self.manual_frame = ttk.Frame(self)
        self.manual_frame.pack(pady=5, fill="x")

        self.acelerador_switch = ttk.Checkbutton(self.manual_frame, text="Acelerador Encendido", variable=acelerador_on, command=publicar_control)
        self.freno_switch = ttk.Checkbutton(self.manual_frame, text="Freno Presionado", variable=freno_on, command=publicar_control)

        # Por defecto ocultos (modo automático)
        self.manual_frame.pack_forget()

        # Gráficos
        self.fig, (self.ax_rpm, self.ax_vel, self.ax_gear) = plt.subplots(3, 1, figsize=(6, 8))
        plt.tight_layout()

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack()

        self.update_graphs()  # Primera llamada para iniciar actualización

    def toggle_manual(self):
        if modo_manual.get():
            self.manual_frame.pack(pady=5, fill="x")
            self.acelerador_switch.pack(side="left", padx=10)
            self.freno_switch.pack(side="left", padx=10)
        else:
            self.manual_frame.pack_forget()
            acelerador_on.set(False)
            freno_on.set(False)
            publicar_control()  # publicar con valores 0

    def update_graphs(self):
        # Limpiar eplotear datos
        self.ax_rpm.clear()
        self.ax_vel.clear()
        self.ax_gear.clear()

        self.ax_rpm.plot(timestamps, rpm_data, marker='o', linestyle='-', color='b')
        self.ax_rpm.set_title("RPM del Motor")
        self.ax_rpm.set_xlabel("Tiempo")
        self.ax_rpm.set_ylabel("RPM")

        self.ax_vel.plot(timestamps, vel_lineal_data, marker='o', linestyle='-', color='g')
        self.ax_vel.set_title("Velocidad Lineal (km/h)")
        self.ax_vel.set_xlabel("Tiempo")
        self.ax_vel.set_ylabel("Velocidad")

        self.ax_gear.plot(timestamps, gear_data, marker='o', linestyle='-', color='r')
        self.ax_gear.set_title("Marcha")
        self.ax_gear.set_xlabel("Tiempo")
        self.ax_gear.set_ylabel("Gear")

        self.fig.autofmt_xdate(rotation=45)
        self.canvas.draw()

        # Actualizar cada segundo
        self.after(1000, self.update_graphs)

if __name__ == '__main__':
    app = TractorDashboard()
    app.mainloop()
