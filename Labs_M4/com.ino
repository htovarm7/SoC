#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

const char* ssid = "Equipo6";
const char* password = "Guajardo";
const char* mqtt_server = "192.168.137.214";

WiFiClient espClient;
PubSubClient client(espClient);

float velocidad_angular = 0.0;
float relacion_transmision = 0.0;
float radio_rueda = 0.0;

void setup_wifi() {
  delay(10);
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("WiFi connected");
}

void callback(char* topic, byte* payload, unsigned int length) {
  payload[length] = '\0';
  String message = String((char*)payload);
  Serial.println("Received: " + message);

  StaticJsonDocument<200> doc;
  DeserializationError error = deserializeJson(doc, message);
  if (!error) {
    velocidad_angular = doc["velocidad_angular"];
    relacion_transmision = doc["relacion_transmision"];
    radio_rueda = doc["radio_rueda"];
  }
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("ESP8266Client")) {
      client.subscribe("tractor/inputs");
    } else {
      delay(5000);
    }
  }
}

void setup() {
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Simulación de cálculos
  float rpm = velocidad_angular * 60 / (2 * 3.1416);
  float vel_lineal = velocidad_angular * radio_rueda / relacion_transmision;

  StaticJsonDocument<200> doc;
  doc["rpm"] = rpm;
  doc["vel_lineal"] = vel_lineal;

  char buffer[256];
  serializeJson(doc, buffer);
  client.publish("tractor/outputs", buffer);

  delay(2000); // Espera entre envíos
}
