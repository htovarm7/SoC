import tkinter as tk
from tkinter import ttk
import threading
import json
from datetime import datetime
import time
import paho.mqtt.client as mqtt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# === MQTT Configuration ===
broker_address   = "192.168.137.59"
topic_sub        = "tractor/data"
topic_control    = "tractor/control"

# === Data containers ===
time_data        = []
rpm_data         = []
vel_lineal_data  = []
gear_data        = []

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc, properties=None):
    """Callback when the client connects to the MQTT broker."""
    print("✅ MQTT connected with code", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    """Callback when a message is received from the MQTT broker."""
    try:
        payload = json.loads(msg.payload.decode())
        # Ensure all required keys are present
        if all(k in payload for k in ("rpm", "velocity", "gear")):
            t = time.time()
            time_data.append(t)
            rpm_data.append(payload["rpm"])
            vel_lineal_data.append(payload["velocity"])
            gear_data.append(payload["gear"])
            print(f"🕒 {datetime.now().strftime('%H:%M:%S')}  rpm={payload['rpm']} vel={payload['velocity']} gear={payload['gear']}")
    except Exception as e:
        print("⚠ Error processing MQTT:", e)

# === Initialize MQTT Client ===
mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message
mqtt_client.connect(broker_address, 1883, 60)
# Run MQTT loop in a separate thread to avoid blocking the GUI
threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()

# === Tkinter GUI Setup ===
root = tk.Tk()
root.title("Tractor Dashboard")

# === Control Variables ===
manual_mode  = tk.BooleanVar(value=False)
throttle_on  = tk.BooleanVar(value=False)
brake_on     = tk.BooleanVar(value=False)

# === Controls Frame ===
ctrl_frame = ttk.Frame(root, padding=10)
ctrl_frame.pack(fill=tk.X)

# Manual controls frame (hidden by default)
manual_frame = ttk.Frame(root, padding=5, relief=tk.RIDGE)

def toggle_manual_controls():
    """Show or hide manual controls based on manual_mode."""
    if manual_mode.get():
        manual_frame.pack(fill=tk.X, pady=5)
    else:
        manual_frame.pack_forget()
        # Reset throttle and brake when exiting manual mode
        throttle_on.set(False)
        brake_on.set(False)
        publish_control()

# Manual mode switch
ttk.Checkbutton(
    ctrl_frame, text="Manual Mode",
    variable=manual_mode,
    command=toggle_manual_controls
).pack(side=tk.LEFT, padx=5)

# Throttle and brake controls (only visible in manual mode)
ttk.Checkbutton(
    manual_frame, text="Throttle",
    variable=throttle_on,
    command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)
ttk.Checkbutton(
    manual_frame, text="Brake",
    variable=brake_on,
    command=lambda: publish_control()
).pack(side=tk.LEFT, padx=10)

# === Matplotlib Plot Setup ===
fig = Figure(figsize=(6, 6), dpi=100)
ax_rpm  = fig.add_subplot(311)
ax_vel  = fig.add_subplot(312)
ax_gear = fig.add_subplot(313)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

def publish_control():
    """Publish throttle and brake control messages via MQTT."""
    if manual_mode.get():
        msg = {
            "throttle": 100 if throttle_on.get() else 0,
            "brake":    100 if brake_on.get()    else 0
        }
        mqtt_client.publish(topic_control, json.dumps(msg))
        print("📤 Control published:", msg)

def update_plot():
    """Update the plots with the latest data."""
    if not time_data:
        root.after(200, update_plot)
        return

    n = min(len(time_data), len(rpm_data), len(vel_lineal_data), len(gear_data))
    t0 = time_data[0]
    t_rel = [t - t0 for t in time_data[:n]]

    ax_rpm.clear(); ax_vel.clear(); ax_gear.clear()

    ax_rpm.plot(t_rel, rpm_data[:n], label="RPM", color='blue')
    ax_rpm.set_title("Engine RPM")
    ax_rpm.set_ylabel("RPM")
    ax_rpm.legend()

    ax_vel.plot(t_rel, vel_lineal_data[:n], label="Linear Velocity", color='green')
    ax_vel.set_title("Linear Velocity")
    ax_vel.set_ylabel("m/s")
    ax_vel.legend()

    ax_gear.plot(t_rel, gear_data[:n], label="Gear", color='red', marker='o')
    ax_gear.set_title("Current Gear")
    ax_gear.set_ylabel("Gear")
    ax_gear.legend()

    fig.tight_layout()
    canvas.draw()

    root.after(200, update_plot)

# Start the periodic plot update loop
root.after(200, update_plot)

def on_closing():
    """Clean up resources on window close."""
    mqtt_client.loop_stop()
    mqtt_client.disconnect()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()