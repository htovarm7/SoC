import paho.mqtt.client as mqtt
import json
import csv
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import threading
from datetime import datetime

# ========== Configuración MQTT ==========
broker_address = "localhost"  # Cambia por la IP de tu ESP32 o broker real
topic_pub = "tractor/inputs"  # Topic para enviar al ESP32
topic_sub = "tractor/data"    # Topic para recibir del ESP32

# ========== Datos almacenados ==========
rpm_data = []
vel_lineal_data = []
gear_data = []
timestamps = []

CSV_FILENAME = "tractor_behavior.csv"
CSV_HEADER = ["timestamp", "rpm", "velocidad_lineal", "gear"]

def write_to_csv(timestamp, rpm, vl, gear):
    with open(CSV_FILENAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if csvfile.tell() == 0:
            writer.writerow(CSV_HEADER)
        writer.writerow([timestamp, f"{rpm:.2f}", f"{vl:.2f}", gear])

# ========== Callbacks MQTT ==========
def on_connect(client, userdata, flags, rc):
    print("Conectado con código: " + str(rc))
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        rpm = data.get("rpm")
        vl = data.get("spd")  # CAMBIO: antes era 'vl'
        gear = data.get("gear")
        now = datetime.now().strftime("%H:%M:%S")

        if rpm is not None and vl is not None:
            rpm_data.append(rpm)
            vel_lineal_data.append(vl)
            gear_data.append(gear)
            timestamps.append(now)

            # Limitar a 20 muestras
            if len(rpm_data) > 20:
                rpm_data.pop(0)
                vel_lineal_data.pop(0)
                gear_data.pop(0)
                timestamps.pop(0)

            write_to_csv(now, rpm, vl, gear)

            # === Gráficas ===
            plt.clf()

            plt.subplot(3, 1, 1)
            plt.plot(timestamps, rpm_data, 'b-o', label='RPM')
            plt.title("RPM del Tractor")
            plt.ylabel("RPM")
            plt.grid(True)
            plt.legend()

            plt.subplot(3, 1, 2)
            plt.plot(timestamps, vel_lineal_data, 'g-x', label='Velocidad (km/h)')
            plt.ylabel("Velocidad")
            plt.grid(True)
            plt.legend()

            plt.subplot(3, 1, 3)
            plt.plot(timestamps, gear_data, 'r-s', label='Marcha')
            plt.xlabel("Tiempo")
            plt.ylabel("Gear")
            plt.grid(True)
            plt.legend()

            plt.tight_layout()
            plt.draw()
            plt.pause(0.1)

    except Exception as e:
        print("❌ Error al procesar el mensaje:", e)

# ========== Envío de comandos ==========
def send_data(vel_angular, trans_ratio, wheel_radius):
    data = {
        "velocidad_angular": vel_angular,
        "relacion_transmision": trans_ratio,
        "radio_rueda": wheel_radius
    }
    client.publish(topic_pub, json.dumps(data))
    print(f"✅ Datos enviados: {data}")

# ========== Cliente MQTT ==========
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def mqtt_loop():
    client.loop_forever()

mqtt_thread = threading.Thread(target=mqtt_loop)
mqtt_thread.daemon = True
mqtt_thread.start()

# ========== GUI ==========
layout = [
    [sg.Text('Velocidad Angular (rad/s)'), sg.InputText(key='-VEL-')],
    [sg.Text('Relación de Transmisión'), sg.InputText(key='-TRANS-')],
    [sg.Text('Radio de la Rueda (m)'), sg.InputText(key='-RAD-')],
    [sg.Button('Enviar')]
]

window = sg.Window('Control del Tractor', layout)
plt.ion()
plt.figure(figsize=(10, 8))
plt.show()

# ========== Loop principal ==========
while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Enviar':
        try:
            vel_ang = float(values['-VEL-'])
            trans = float(values['-TRANS-'])
            radius = float(values['-RAD-'])
            send_data(vel_ang, trans, radius)
        except:
            print("⚠️ Entrada inválida. Asegúrate de ingresar números.")

window.close()
client.loop_stop()
client.disconnect()
plt.ioff()
plt.show()