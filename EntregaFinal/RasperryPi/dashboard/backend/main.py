from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import paho.mqtt.client as mqtt
import json
import asyncio

app = FastAPI()

# Configurar CORS para que React pueda comunicarse con este backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto a tu dominio en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lista de websockets conectados
websockets = []

# Dirección del broker y topic
broker_address = "192.168.137.59"
topic_sub = "tractor/data"

# Función que envía datos a todos los websockets conectados
async def broadcast_data(data):
    for ws in websockets:
        try:
            await ws.send_text(json.dumps(data))
        except:
            pass

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Conectado al broker MQTT")
        client.subscribe(topic_sub)
    else:
        print("❌ Error al conectar. Código:", rc)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("📥 Mensaje MQTT:", data)
        asyncio.run(broadcast_data(data))
    except Exception as e:
        print("⚠️ Error al procesar el mensaje:", e)

# Inicializar MQTT
mqtt_client = mqtt.Client()
mqtt_client.on_connect = on_connect
mqtt_client.on_message = on_message

def start_mqtt():
    try:
        mqtt_client.connect(broker_address, 1883, 60)
        mqtt_client.loop_start()
    except Exception as e:
        print("🚫 Error al conectar con el broker MQTT:", e)

@app.on_event("startup")
async def startup_event():
    start_mqtt()

# WebSocket endpoint para el frontend
@app.websocket("/ws/data")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websockets.append(websocket)
    print("🔌 Cliente conectado por WebSocket.")
    try:
        while True:
            await websocket.receive_text()  # mantener la conexión viva
    except:
        websockets.remove(websocket)
        print("❌ Cliente desconectado.")
