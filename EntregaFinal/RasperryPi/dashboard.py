#!/usr/bin/env python3

import sys

import json

import threading

from datetime import datetime



import paho.mqtt.client as mqtt

from PySide6 import QtWidgets, QtCore

import pyqtgraph as pg



# === MQTT Setup ===

BROKER    = "192.168.137.59"

TOPIC_SUB = "tractor/data"

TOPIC_PUB = "tractor/control"



rpm_data   = []

vel_data   = []

gear_data  = []

timestamps = []



class TractorDashboard(QtWidgets.QMainWindow):

    def _init_(self):

        super()._init_()

        self.setWindowTitle("Dashboard del Tractor")

        self.resize(1000, 600)



        central = QtWidgets.QWidget()

        self.setCentralWidget(central)

        vbox = QtWidgets.QVBoxLayout(central)



        # — Controles Manual/Auto —

        hbox = QtWidgets.QHBoxLayout()

        self.chk_manual   = QtWidgets.QCheckBox("Modo Manual")

        self.chk_throttle = QtWidgets.QCheckBox("Acelerador")

        self.chk_brake    = QtWidgets.QCheckBox("Freno")

        self.chk_throttle.setEnabled(False)

        self.chk_brake.setEnabled(False)

        hbox.addWidget(self.chk_manual)

        hbox.addWidget(self.chk_throttle)

        hbox.addWidget(self.chk_brake)

        vbox.addLayout(hbox)



        self.chk_manual.stateChanged.connect(self.on_manual_toggled)

        self.chk_throttle.stateChanged.connect(self.publish_control)

        self.chk_brake.stateChanged.connect(self.publish_control)



        # — Gráficas con pyqtgraph —

        pg.setConfigOptions(antialias=True)

        self.plot_rpm  = pg.PlotWidget(title="RPM del Motor")

        self.plot_vel  = pg.PlotWidget(title="Velocidad Lineal (km/h)")

        self.plot_gear = pg.PlotWidget(title="Marcha")

        for pw in (self.plot_rpm, self.plot_vel, self.plot_gear):

            pw.showGrid(x=True, y=True)



        self.curve_rpm  = self.plot_rpm.plot(pen='y', symbol='o')

        self.curve_vel  = self.plot_vel.plot(pen='c', symbol='o')

        self.curve_gear = self.plot_gear.plot(pen='m', symbol='o')



        vbox.addWidget(self.plot_rpm)

        vbox.addWidget(self.plot_vel)

        vbox.addWidget(self.plot_gear)



        # Timer para refrescar gráficas

        timer = QtCore.QTimer(self)

        timer.timeout.connect(self.update_plots)

        timer.start(500)  # cada 500 ms



    def on_manual_toggled(self, state):

        ena = state == QtCore.Qt.Checked

        self.chk_throttle.setEnabled(ena)

        self.chk_brake.setEnabled(ena)

        if not ena:

            self.chk_throttle.setChecked(False)

            self.chk_brake.setChecked(False)



    def publish_control(self):

        if self.chk_manual.isChecked():

            payload = json.dumps({

                "throttle": 100 if self.chk_throttle.isChecked() else 0,

                "brake":    100 if self.chk_brake.isChecked()    else 0

            })

            mqtt_client.publish(TOPIC_PUB, payload)

            print("📤 Control publicado:", payload)



    def update_plots(self):

        if not timestamps:

            return

        # X como segundos desde el primer timestamp

        x = [(t - timestamps[0]).total_seconds() for t in timestamps]

        self.curve_rpm.setData(x, rpm_data)

        self.curve_vel.setData(x, vel_data)

        self.curve_gear.setData(x, gear_data)



def on_connect(client, userdata, flags, rc, properties=None):

    print("✅ MQTT conectado, código:", rc)

    client.subscribe(TOPIC_SUB)



def on_message(client, userdata, msg):

    try:

        data = json.loads(msg.payload.decode())

        if all(k in data for k in ("rpm","spd","gear")):

            now = datetime.now()

            rpm_data.append(data["rpm"])

            vel_data.append(data["spd"])

            gear_data.append(data["gear"])

            timestamps.append(now)

            print(f"🕒 {now.strftime('%H:%M:%S')} → rpm={data['rpm']}, spd={data['spd']}, gear={data['gear']}")

    except Exception as e:

        print("⚠ Error procesando mensaje:", e)



# === Inicializar MQTT ===

mqtt_client = mqtt.Client(protocol=mqtt.MQTTv311)

mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message

mqtt_client.connect(BROKER, 1883, 60)

threading.Thread(target=mqtt_client.loop_forever, daemon=True).start()



# === Lanzar la app ===

if _name_ == "_main_":

    app = QtWidgets.QApplication(sys.argv)

    win = TractorDashboard()

    win.show()

    sys.exit(app.exec())