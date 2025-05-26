#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "TU_SSID";
const char* password = "TU_PASSWORD";
const char* mqtt_server = "TU_IP_RASPBERRY";  // IP local, ejemplo: "192.168.1.100"

WiFiClient espClient;
PubSubClient client(espClient);

long lastMsg = 0;
int velocidad = 0;
int rpm = 0;
int velocidad_deseada = 0;

void callback(char* topic, byte* payload, unsigned int length) {
  String value = "";
  for (int i = 0; i < length; i++) {
    value += (char)payload[i];
  }
  velocidad_deseada = value.toInt();
}

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
      client.subscribe("control/input");
    } else {
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  long now = millis();
  if (now - lastMsg > 2000) { // cada 2 segundos
    lastMsg = now;

    velocidad = velocidad_deseada;  // Simulación directa
    rpm = velocidad * 30;           // Relación ficticia

    String payload = "{\"velocidad\": " + String(velocidad) + ", \"rpm\": " + String(rpm) + "}";
    client.publish("sensor/data", payload.c_str());
  }
}
