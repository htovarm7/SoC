import paho.mqtt.client as mqtt
import json

broker_address = "192.168.137.59"
topic_sub = "tractor/outputs"

def on_connect(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("✅ Conectado correctamente al broker MQTT.")
        client.subscribe(topic_sub)
    else:
        print("❌ Fallo al conectar. Código de error:", reason_code)

def on_message(client, userdata, msg):
    print("\n📥 Mensaje recibido:")
    try:
        data = json.loads(msg.payload.decode())
        print("📊 Datos decodificados:", data)
    except Exception as e:
        print("⚠️ Error al procesar mensaje:", e)

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

try:
    client.connect(broker_address, 1883, 60)
    client.loop_forever()
except Exception as e:
    print("🚫 Error al conectar con el broker MQTT:", e)
