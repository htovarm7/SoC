#include <ESP8266WiFi.h>  // Usar #include <WiFi.h> para ESP32
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Configuración WiFi
const char* ssid = "Equipo6";
const char* password = "Guajardo";

// Configuración MQTT
const char* mqtt_server = "IP_RASPBERRY_PI";
const char* topic_sub = "tractor/inputs";
const char* topic_pub = "tractor/outputs";

// Variables del modelo
float velocidad_angular = 10.0;  // rad/s
float relacion_transmision = 0.1;
float radio_rueda = 0.3;  // metros

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Dirección IP: ");
  Serial.println(WiFi.localIP());
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensaje recibido [");
  Serial.print(topic);
  Serial.print("] ");
  
  // Parsear el mensaje JSON recibido
  DynamicJsonDocument doc(256);
  deserializeJson(doc, payload, length);
  
  // Actualizar variables del modelo
  velocidad_angular = doc["velocidad_angular"] | velocidad_angular;
  relacion_transmision = doc["relacion_transmision"] | relacion_transmision;
  radio_rueda = doc["radio_rueda"] | radio_rueda;
  
  Serial.print("Nuevos parámetros: ");
  Serial.print("VelAng=");
  Serial.print(velocidad_angular);
  Serial.print(" rad/s, Trans=");
  Serial.print(relacion_transmision);
  Serial.print(", Rueda=");
  Serial.print(radio_rueda);
  Serial.println(" m");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Intentando conexión MQTT...");
    
    if (client.connect("ESP8266Client")) {  // Cambiar por "ESP32Client" para ESP32
      Serial.println("conectado");
      client.subscribe(topic_sub);
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      Serial.println(" intentando de nuevo en 5 segundos");
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

  // Calcular RPM y velocidad lineal según el modelo
  float rpm = velocidad_angular * (60.0 / (2.0 * PI)) * relacion_transmision;
  float velocidad_lineal = velocidad_angular * relacion_transmision * radio_rueda;
  
  // Crear mensaje JSON
  DynamicJsonDocument doc(256);
  doc["rpm"] = rpm;
  doc["vel_lineal"] = velocidad_lineal;
  
  char buffer[256];
  serializeJson(doc, buffer);
  
  // Publicar datos
  client.publish(topic_pub, buffer);
  
  Serial.print("Datos enviados: RPM=");
  Serial.print(rpm);
  Serial.print(", VelLin=");
  Serial.print(velocidad_lineal);
  Serial.println(" m/s");
  
  delay(1000);  // Esperar 1 segundo entre publicaciones
}