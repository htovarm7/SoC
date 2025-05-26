import streamlit as st
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
import json
import csv
import threading
import time
from collections import deque

# MQTT Configuration
broker_address = "localhost"
topic_pub = "tractor/inputs"
topic_sub = "tractor/outputs"

# Data storage
rpm_data = deque(maxlen=50)
vel_lineal_data = deque(maxlen=50)

# CSV file
csv_file = "datos_tractor.csv"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data["rpm"]
        vel_lineal = data["vel_lineal"]

        rpm_data.append(rpm)
        vel_lineal_data.append(vel_lineal)

        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([rpm, vel_lineal])
    except Exception as e:
        print("Error handling message:", e)

# MQTT Client
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

# Streamlit UI
st.set_page_config(page_title="Tractor Dashboard", layout="centered")
st.title("🚜 Tractor Control Dashboard")

st.sidebar.header("Input Parameters")

vel_angular = st.sidebar.number_input("Angular Velocity (rad/s)", min_value=0.0, step=0.1)
trans_ratio = st.sidebar.number_input("Transmission Ratio", min_value=0.1, step=0.1)
wheel_radius = st.sidebar.number_input("Wheel Radius (m)", min_value=0.0, step=0.01)

if st.sidebar.button("Send"):
    data = {
        "velocidad_angular": vel_angular,
        "relacion_transmision": trans_ratio,
        "radio_rueda": wheel_radius
    }
    client.publish(topic_pub, json.dumps(data))
    st.sidebar.success(f"Sent: {data}")
    # Forzar actualización de las gráficas
    st.experimental_rerun()

# Área de actualización automática
st.subheader("📊 RPM and Linear Velocity (Live)")

# Usar st.empty() para el contenedor de gráficas
plot_placeholder = st.empty()

# Función para actualizar gráficas
def update_plots():
    with plot_placeholder.container():
        if rpm_data or vel_lineal_data:  # Solo dibujar si hay datos
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 6))

            if rpm_data:
                ax1.plot(list(rpm_data), label="RPM", color='tab:blue')
                ax1.set_ylabel("RPM")
                ax1.set_title("RPM")
                ax1.grid(True)

            if vel_lineal_data:
                ax2.plot(list(vel_lineal_data), label="Linear Velocity (m/s)", color='tab:green')
                ax2.set_ylabel("Velocity")
                ax2.set_title("Linear Velocity")
                ax2.grid(True)

            st.pyplot(fig)
        else:
            st.warning("Waiting for data...")

# Bucle principal de la aplicación
while True:
    update_plots()
    time.sleep(1)  # Espera 1 segundo antes de actualizar