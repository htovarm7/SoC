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
