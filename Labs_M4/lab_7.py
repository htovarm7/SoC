import paho.mqtt.client as mqtt
import json
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import csv
import threading
from queue import Queue
import time

# Configuración MQTT
broker_address = "localhost"  # Cambiar si el broker está en otra máquina
topic_pub = "tractor/inputs"
topic_sub = "tractor/outputs"

# Variables para el modelo y gráficos
rpm_data = []
vel_lineal_data = []
data_queue = Queue()  # Cola para comunicación entre threads

# Configuración del cliente MQTT
client = mqtt.Client()

# Función para manejar conexión MQTT
def on_connect(client, userdata, flags, rc):
    print("Conectado al broker con código: " + str(rc))
    client.subscribe(topic_sub)

# Función para manejar mensajes recibidos (ejecutada en otro thread)
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print(f"Datos recibidos: {data}")
        data_queue.put(data)  # Ponemos los datos en la cola para el thread principal
    except Exception as e:
        print(f"Error procesando mensaje: {e}")

# Función para procesar datos en segundo plano
def data_processing_thread():
    while True:
        if not data_queue.empty():
            data = data_queue.get()
            
            # Procesar datos
            rpm = data.get("rpm", 0)
            vel_lineal = data.get("vel_lineal", 0)
            
            # Guardar en listas para gráficos
            rpm_data.append(rpm)
            vel_lineal_data.append(vel_lineal)
            
            # Guardar en archivo CSV
            with open('datos_tractor.csv', mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([time.time(), rpm, vel_lineal])
            
            # Actualizar gráficos
            update_plots()

# Función para actualizar gráficos
def update_plots():
    plt.clf()
    
    # Gráfico de RPM
    plt.subplot(2, 1, 1)
    plt.plot(rpm_data, 'r-', label='RPM')
    plt.xlabel('Mediciones')
    plt.ylabel('Revoluciones por minuto')
    plt.title('RPM del Motor')
    plt.grid(True)
    plt.legend()
    
    # Gráfico de velocidad lineal
    plt.subplot(2, 1, 2)
    plt.plot(vel_lineal_data, 'b-', label='Velocidad Lineal (m/s)')
    plt.xlabel('Mediciones')
    plt.ylabel('Velocidad (m/s)')
    plt.title('Velocidad Lineal del Tractor')
    plt.grid(True)
    plt.legend()
    
    plt.tight_layout()
    plt.draw()
    plt.pause(0.01)

# Función para enviar datos al microcontrolador
def send_data(vel_angular, trans_ratio, wheel_radius):
    data = {
        "velocidad_angular": vel_angular,
        "relacion_transmision": trans_ratio,
        "radio_rueda": wheel_radius
    }
    client.publish(topic_pub, json.dumps(data))
    print(f"Datos enviados: {data}")

# Configuración de la interfaz gráfica
layout = [
    [sg.Text('Control del Modelo de Tractor', font=('Helvetica', 16))],
    [sg.Text('Velocidad Angular (rad/s):'), sg.InputText('10', key='-VEL-', size=(10,1))],
    [sg.Text('Relación de Transmisión:'), sg.InputText('0.1', key='-TRANS-', size=(10,1))],
    [sg.Text('Radio de Rueda (m):'), sg.InputText('0.3', key='-RAD-', size=(10,1))],
    [sg.Button('Enviar', size=(10,1)), sg.Button('Salir', size=(10,1))],
    [sg.Text('Últimos datos recibidos:', font=('Helvetica', 12))],
    [sg.Multiline(size=(50,5), key='-OUTPUT-', autoscroll=True, disabled=True)],
    [sg.Text('Gráficos en tiempo real:', font=('Helvetica', 12))],
]

window = sg.Window('Dashboard de Control de Tractor', layout, finalize=True)

# Configurar MQTT
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)
client.loop_start()

# Configurar matplotlib en modo interactivo
plt.ion()
fig = plt.figure(figsize=(10, 6))
plt.show()

# Iniciar thread para procesamiento de datos
processing_thread = threading.Thread(target=data_processing_thread, daemon=True)
processing_thread.start()

# Bucle principal de la interfaz
while True:
    event, values = window.read(timeout=100)
    
    if event == sg.WIN_CLOSED or event == 'Salir':
        break
        
    if event == 'Enviar':
        try:
            vel_angular = float(values['-VEL-'])
            trans_ratio = float(values['-TRANS-'])
            wheel_radius = float(values['-RAD-'])
            send_data(vel_angular, trans_ratio, wheel_radius)
        except ValueError:
            sg.popup_error("Por favor ingrese valores numéricos válidos")

# Limpieza al salir
client.loop_stop()
client.disconnect()
window.close()
plt.ioff()