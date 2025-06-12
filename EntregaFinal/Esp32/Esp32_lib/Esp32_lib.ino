#include "EngTrModel.h"      // Model header
#include "rtwtypes.h"
#include <serial-readline.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#include <PubSubClient.h>


const char* WIFI_SSID = WIFI_SSID;
const char* WIFI_PASS = WIFI_PASS;
const char* MQTT_SERVER = MQTT_SERVER;
const int MQTT_PORT = MQTT_PORT;


const char* MQTT_CLIENT_ID = MQTT_CLIENT_ID;
const char* MQTT_TOPIC = MQTT_TOPIC;

// Global objects
WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

// Serial line reader and JSON document
void onSerialLineReceived(char*);
SerialLineReader serialReader(Serial, onSerialLineReceived);
JsonDocument jsonDoc;

// Input variables
int adcValue = 0;
int throttleInput = 0;
int buttonState = 0;

// Callback for serial line reception
void onSerialLineReceived(char *line) {
  deserializeJson(jsonDoc, line);
  adcValue = jsonDoc["adc"];
  buttonState = jsonDoc["button"];
}

// Connects to WiFi network
void connectToWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

// Ensures MQTT connection
void ensureMQTTConnection() {
  while (!mqttClient.connected()) {
    mqttClient.connect(MQTT_CLIENT_ID);
    if (!mqttClient.connected()) {
      delay(5000);
    }
  }
}

// Arduino setup function
void setup() {
  delay(3000);
  Serial.begin(9600);
  connectToWiFi();
  mqttClient.setServer(MQTT_SERVER, MQTT_PORT);
  EngTrModel_initialize();
}

// Arduino main loop
void loop() { 
  if (!mqttClient.connected()) {
    ensureMQTTConnection();
  }
  mqttClient.loop();
  serialReader.poll();

  // Map ADC value to throttle input (0-200)
  throttleInput = map(adcValue, 0, 4095, 0, 200);
  EngTrModel_U.Throttle = throttleInput > 0 ? throttleInput : 0.0;
  EngTrModel_U.BrakeTorque = buttonState ? 10000.0 : 0.0;

  // Run model step
  EngTrModel_step();

  // Prepare and publish MQTT message
  String mqttMessage = String("{\"velocity\":") + EngTrModel_Y.VehicleSpeed +
                       ",\"rpm\":" + EngTrModel_Y.EngineSpeed +
                       ",\"gear\":" + EngTrModel_Y.Gear + "}";
  mqttClient.publish(MQTT_TOPIC, mqttMessage.c_str());

  // Print model outputs to serial
  Serial.print(EngTrModel_Y.VehicleSpeed);
  Serial.print("V");
  Serial.print(EngTrModel_Y.EngineSpeed);
  Serial.print("S");
  Serial.print(EngTrModel_Y.Gear);
  Serial.print("E");

  delay(200);
}
