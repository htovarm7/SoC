import pandas as pd
import random
import math
import time
import matplotlib.pyplot as plt
import PySimpleGUI as sg

# Función para calcular RPM
def calcular_rpm(velocidad_angular, radio_rueda, relacion_transmision):
    return (velocidad_angular * 60) / (2 * math.pi * radio_rueda * relacion_transmision)

# Generación de datos aleatorios
def generar_datos():
    velocidad_angular = random.uniform(5, 15)  # rad/s
    radio_rueda = random.uniform(0.3, 0.7)    # metros
    relacion_transmision = 10                 # constante
    rpm = calcular_rpm(velocidad_angular, radio_rueda, relacion_transmision)
    return velocidad_angular, radio_rueda, relacion_transmision, rpm

# Guardar datos en CSV
def guardar_datos_csv(datos, archivo="datos_tractor.csv"):
    df = pd.DataFrame(datos, columns=["Velocidad Angular", "Radio Rueda", "Relación Transmisión", "RPM"])
    df.to_csv(archivo, index=False)

# Visualización gráfica
def graficar_datos(datos):
    velocidades = [d[0] for d in datos]
    rpms = [d[3] for d in datos]
    plt.plot(velocidades, rpms, label="RPM vs Velocidad Angular")
    plt.xlabel("Velocidad Angular (rad/s)")
    plt.ylabel("RPM")
    plt.legend()
    plt.show()

# Interfaz gráfica con PySimpleGUI
def interfaz_grafica():
    layout = [[sg.Text("Simulación del Tractor")],
              [sg.Button("Iniciar"), sg.Button("Detener")]]
    window = sg.Window("Simulación Tractor", layout)
    datos = []
    while True:
        event, _ = window.read(timeout=1000)
        if event == sg.WINDOW_CLOSED or event == "Detener":
            break
        if event == "Iniciar":
            nuevo_dato = generar_datos()
            datos.append(nuevo_dato)
            guardar_datos_csv(datos)
            graficar_datos(datos)
    window.close()

# Ejecutar programa
if __name__ == "__main__":
    interfaz_grafica()