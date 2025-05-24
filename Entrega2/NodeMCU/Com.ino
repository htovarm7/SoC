"""
 * @file com.ino
 * @date 17/5/2025
 * @author Hector Tovar
 * 
 * @brief This code is for the ESP8266 to send data to a Raspberry Pi using MQTT.
 * The ESP8266 reads data from the STM32 via UART and sends it to the Raspberry Pi.
 * The Raspberry Pi will then process the data and send it to the cloud.
"""

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// WiFi configuration
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// MQTT
const char* mqtt_server = "RPI_IP_ADDRESS";
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
String inputData = "";

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client")) {
      // Connected
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(9600); // UART with STM32
  setup_wifi();
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (Serial.available()) {
    inputData = Serial.readStringUntil('\n');
    client.publish("tractor/data", inputData.c_str());
  }
}
