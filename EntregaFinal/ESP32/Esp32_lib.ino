#include "EngTrModel.h"      // Model header
#include "rtwtypes.h"
#include <serial-readline.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi and MQTT configuration
const char* WIFI_SSID = "EQUIPO6";
const char* WIFI_PASS = "Guajardo";
const char* MQTT_SERVER = "192.168.137.59";
const int   MQTT_PORT = 1883;

// Control mode: "dashboard" or "manual"
String g_controlMode = "dashboard";

// WiFi and MQTT clients
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Serial line reader and JSON document
void onSerialReceived(char*);
SerialLineReader serialReader(Serial, onSerialReceived);
JsonDocument serialDoc;

// Input variables from UART
int adcValue = 0;
int mappedThrottle = 0;
int buttonState = 0;

// Handle incoming serial line (UART)
void onSerialReceived(char *line) {
  deserializeJson(serialDoc, line);
  adcValue = serialDoc["adc"];
  buttonState = serialDoc["button"];
}

// Connect to WiFi
void connectWiFi() {
  delay(10);
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

// Reconnect to MQTT broker if disconnected
void reconnectMQTT() {
  while (!mqttClient.connected()) {
    if (mqttClient.connect("stm32client")) {
      mqttClient.subscribe("tractor/control");
    } else {
      Serial.print(mqttClient.state());
      delay(5000);
    }
  }
}

// Handle incoming MQTT messages
void mqttCallback(char* topic, byte* payload, unsigned int length) {
  DynamicJsonDocument msgDoc(128);
  DeserializationError err = deserializeJson(msgDoc, payload, length);
  if (err) return;

  String topicStr = String(topic);
  if (topicStr == "tractor/control") {
    const char* mode  = msgDoc["mode"];
    bool pedal        = msgDoc["pedal"];
    bool brake        = msgDoc["brake"];
    g_controlMode = String(mode);
    // Apply control to model in manual mode
    if (g_controlMode == "manual") {
      EngTrModel_U.Throttle    = pedal ? 200.0 : 0.0;
      EngTrModel_U.BrakeTorque = brake ? 10000.0 : 0.0;
    }
  }
}

// Arduino setup function
void setup() {
  delay(3000);
  Serial.begin(9600);
  connectWiFi();
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  mqttClient.setCallback(mqttCallback);
  EngTrModel_initialize();
}

// Arduino main loop
void loop() { 
  if (!mqttClient.connected()) {
    reconnectMQTT();
  }
  mqttClient.loop();
  serialReader.poll();

  // Dashboard mode: use UART inputs
  if (g_controlMode == "dashboard") {
    mappedThrottle = map(adcValue, 0, 4095, 0, 200);
    EngTrModel_U.Throttle = (mappedThrottle > 0) ? mappedThrottle : 0.0;
    EngTrModel_U.BrakeTorque = (buttonState ? 10000.0 : 0.0);
  }

  // Step the model
  EngTrModel_step();

  // Publish model outputs via MQTT
  String mqttMsg = String("{\"velocity\":") + EngTrModel_Y.VehicleSpeed +
                   ",\"rpm\":" + EngTrModel_Y.EngineSpeed +
                   ",\"gear\":" + EngTrModel_Y.Gear +"}";
  mqttClient.publish("tractor/data", mqttMsg.c_str());

  // Print model outputs to serial
  Serial.print(EngTrModel_Y.VehicleSpeed);
  Serial.print("V");
  Serial.print(EngTrModel_Y.EngineSpeed);
  Serial.print("S");
  Serial.print(EngTrModel_Y.Gear);
  Serial.print("E");
  delay(200);
}
