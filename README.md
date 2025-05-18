# 🚜 Intelligent Driving System for Agricultural Tractor

This project simulates an intelligent driving system for an agricultural tractor, integrating sensors, actuators, and wireless communication. It is part of an academic challenge developed in collaboration with **John Deere**, using embedded technologies such as **STM32**, **ESP8266**, and **Raspberry Pi**.

## 🎯 Objective

Develop a system that integrates an automatic transmission model, acceleration and brake sensors, and a mechanism for data visualization and storage. The system must collect data from the hardware, process it, and transmit it wirelessly for real-time monitoring.

## 🧩 Project Components

### STM32 (Bare-Metal in C)
- Reads inputs from:
  - **Accelerator** (via potentiometer)
  - **Brake** (via push button)
- Sends sensor data to the ESP8266 over **UART**
- Controls:
  - **4 PWM signals** to represent vehicle speed using LEDs
  - **LCD display** to show acceleration, gear, and vehicle speed
- Receives processed data (RPM, speed, gear) from the ESP8266

### ESP8266 (Firmware in Arduino-style C++)
- Receives UART data from the STM32
- Runs the **automatic transmission control model**
- Sends processed data (RPM, vehicle speed, gear) via **MQTT** to Raspberry Pi

### Raspberry Pi (Python)
- Subscribes to MQTT topics to receive data from the ESP8266
- Stores incoming data in a **CSV file**:
  - Column 1: Engine RPM
  - Column 2: Vehicle Speed
  - Column 3: Gear
- Displays real-time plots using a Python GUI (e.g., **PySimpleGUI**)

## 🧪 Testing and Validation

- Ensure UART communication between STM32 and ESP8266 is reliable
- MQTT messages must be correctly received and parsed by the Raspberry Pi
- Display updates on the LCD must reflect current vehicle state
- Real-time plotting and CSV logging must work simultaneously

## 🔧 Recommended Hardware (for full prototype)

- 4 × DC motors (1:48 ratio)
- 4 × rubber wheels
- 2 × motor drivers (TB6612FNG or L298N)
- 2 × 3.7V Li-ion batteries (2200–5000 mAh)
- 1 × dual 18650 battery holder
- 1 × power supply module for ESP8266
- 1 × LCD (parallel port, not I2C)

## 📌 Notes

- The LCD display must be driven via parallel port (not I2C)
- Delays must be added in `main.c` and `lcd.c` as indicated in comments
- Data should be printed and visualized as decimal values, not just integers

## 👥 Team

| Name               | Username                 |
|-----------------|-----------------------|
| Hector Tovar     | @htovarm7 |
| José Domínguez     | @JLDominguezM |
| Paola Llamas     | @PaolaLlh18|

---

