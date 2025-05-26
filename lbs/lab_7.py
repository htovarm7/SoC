# dashboard.py
import streamlit as st
import paho.mqtt.client as mqtt
import pandas as pd
import time
import json
from datetime import datetime

# MQTT settings
MQTT_BROKER = "localhost"
TOPIC_SUB = "sensor/data"
TOPIC_PUB = "control/input"

# CSV storage
CSV_FILE = "data.csv"

# MQTT callbacks
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_SUB)

def on_message(client, userdata, msg):
    payload = msg.payload.decode()
    try:
        data = json.loads(payload)
        timestamp = datetime.now().isoformat()
        data["timestamp"] = timestamp
        df = pd.DataFrame([data])
        df.to_csv(CSV_FILE, mode='a', header=not os.path.exists(CSV_FILE), index=False)
        st.session_state['latest_data'] = data
    except Exception as e:
        print("Error processing message:", e)

# Init MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER, 1883, 60)
client.loop_start()

# Streamlit UI
st.title("Motor Dashboard - RPi & ESP8266")

# Input for velocity
input_speed = st.number_input("Velocidad deseada", min_value=0, max_value=100, step=1)
if st.button("Enviar al ESP8266"):
    client.publish(TOPIC_PUB, str(input_speed))
    st.success(f"Velocidad {input_speed} enviada")

# Mostrar datos más recientes
if "latest_data" in st.session_state:
    st.subheader("Últimos datos recibidos del ESP8266:")
    st.json(st.session_state["latest_data"])

# Mostrar gráfico (si existe CSV)
try:
    df = pd.read_csv(CSV_FILE)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    st.line_chart(df.set_index('timestamp')[['rpm', 'velocidad']])
except:
    st.warning("No hay datos suficientes aún para graficar.")
