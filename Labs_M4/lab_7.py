import streamlit as st
from streamlit_autorefresh import st_autorefresh
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import json
import csv
import threading
import time
from collections import deque

# === MQTT Configuration ===
broker_address = "localhost"
topic_pub = "tractor/inputs"
topic_sub = "tractor/outputs"

# === Data Storage ===
rpm_data = deque(maxlen=50)
vel_lineal_data = deque(maxlen=50)
csv_file = "datos_tractor.csv"

# === MQTT Callbacks ===
def on_connect(client, userdata, flags, rc):
    print("✅ Connected with result code", rc)
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data.get("rpm", 0)
        vel_lineal = data.get("vel_lineal", 0)

        rpm_data.append(rpm)
        vel_lineal_data.append(vel_lineal)

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([rpm, vel_lineal])
    except Exception as e:
        print("⚠️ Error handling message:", e)

# === MQTT Client ===
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

# Run MQTT loop in background
def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()

# === Streamlit Interface ===
st.set_page_config(page_title="Tractor Dashboard", layout="wide")
st.title("🚜 Tractor Control Dashboard")

# Sidebar for input
st.sidebar.header("📥 Input Parameters")

vel_angular = st.sidebar.number_input("Angular Velocity (rad/s)", min_value=0.0, step=0.1)
trans_ratio = st.sidebar.number_input("Transmission Ratio", min_value=0.1, step=0.1)
wheel_radius = st.sidebar.number_input("Wheel Radius (m)", min_value=0.0, step=0.01)

if st.sidebar.button("Send to ESP8266"):
    data = {
        "velocidad_angular": vel_angular,
        "relacion_transmision": trans_ratio,
        "radio_rueda": wheel_radius
    }
    client.publish(topic_pub, json.dumps(data))
    st.sidebar.success(f"✅ Sent: {data}")

# Realtime graph display
st.subheader("📊 Real-Time RPM and Velocity")

# Dynamic container for plots
plot_container = st.empty()

# Auto-refresh section
run = st.checkbox("🔄 Auto-update graphs", value=True)

# Auto-refresh checkbox
auto_refresh = st.checkbox("🔄 Auto-update graphs")

# Set up auto-refresh every 1 sec (1000 ms)
if auto_refresh:
    st_autorefresh(interval=1000, limit=None, key="autorefresh")

# Gráficas
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6))

ax1.plot(list(rpm_data), label="RPM", color='blue')
ax1.set_ylabel("RPM")
ax1.set_title("Engine RPM")
ax1.grid(True)

ax2.plot(list(vel_lineal_data), label="Velocidad Lineal", color='green')
ax2.set_ylabel("m/s")
ax2.set_title("Velocidad Lineal")
ax2.grid(True)

fig.tight_layout()
st.pyplot(fig)

# CSV Data Preview
st.markdown("---")
if st.checkbox("📄 Show CSV Preview"):
    import pandas as pd
    try:
        df = pd.read_csv(csv_file, names=["RPM", "Velocidad Lineal"])
        st.dataframe(df.tail(10))
    except FileNotFoundError:
        st.warning("⚠️ CSV file not found.")
