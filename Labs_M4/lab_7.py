import paho.mqtt.client as mqtt
import json
import PySimpleGUI as sg
import matplotlib.pyplot as plt
import csv

# MQTT configuration
broker_address = "localhost"
topic_pub = "tractor/inputs"
topic_sub = "tractor/outputs"

rpm_data = []
vel_lineal_data = []

# Callback functions
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe(topic_sub)

def on_message(client, userdata, msg):
    print(f"Message received: {msg.payload.decode()}")
    data = json.loads(msg.payload.decode())
    rpm = data["rpm"]
    vel_lineal = data["vel_lineal"]

    rpm_data.append(rpm)
    vel_lineal_data.append(vel_lineal)

    with open('datos_tractor.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([rpm, vel_lineal])

    plt.clf()
    plt.subplot(2, 1, 1)
    plt.plot(rpm_data, label='RPM')
    plt.xlabel('Measurements')
    plt.ylabel('Revolutions per minute')
    plt.legend()

    plt.subplot(2, 1, 2)
    plt.plot(vel_lineal_data, label='Linear Velocity (m/s)')
    plt.xlabel('Measurements')
    plt.ylabel('Linear Velocity')
    plt.legend()

    plt.pause(0.1)

# MQTT client setup
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_address, 1883, 60)

def send_data(vel_angular, trans_ratio, wheel_radius):
    data = {
        "velocidad_angular": vel_angular,
        "relacion_transmision": trans_ratio,
        "radio_rueda": wheel_radius
    }
    client.publish(topic_pub, json.dumps(data))
    print(f"Data sent: {data}")

# Dashboard
layout = [
    [sg.Text('Angular Velocity (rad/s)'), sg.InputText(key='-VEL-')],
    [sg.Text('Transmission Ratio (engine to wheel)'), sg.InputText(key='-TRANS-')],
    [sg.Text('Wheel Radius (m)'), sg.InputText(key='-RAD-')],
    [sg.Button('Send')]
]
window = sg.Window('Tractor Control', layout)

plt.ion()
plt.show()

client.loop_start()

while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break
    if event == 'Send':
        try:
            vel_angular = float(values['-VEL-'])
            trans_ratio = float(values['-TRANS-'])
            wheel_radius = float(values['-RAD-'])
            send_data(vel_angular, trans_ratio, wheel_radius)
        except ValueError:
            print("Invalid input. Please enter valid numbers.")

window.close()
client.loop_stop()
client.disconnect()
plt.ioff()
plt.show()
