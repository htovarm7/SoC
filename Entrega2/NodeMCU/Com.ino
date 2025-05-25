/**
 * @file com.ino
 * @date 17/5/2025
 * @author Hector Tovar
 * 
 * @brief This code is for the ESP8266 to send data to a Raspberry Pi using MQTT.
 * The ESP8266 reads data from the STM32 via UART and sends it to the Raspberry Pi.
 * The Raspberry Pi will then process the data and send it to the cloud.
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Constants
const float wheel_radius = 0.5; // m
const float transmission_ratio = 10.0;

// WiFi configuration
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// MQTT
const char* mqtt_server = "RPI_IP_ADDRESS";
WiFiClient espClient;
PubSubClient client(espClient);

// Variables
String inputData = "";
float prev_angular_velocity = 0.0;
unsigned long prev_time = 0;

void setup_wifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
}

void reconnect() {
  while (!client.connected()) {
    client.connect("ESP8266Client");
    delay(5000);
  }
}

// Calculates RPM from angular velocity
float calculate_rpm(float angular_velocity) {
  return (angular_velocity * 60.0) / (2.0 * PI * wheel_radius * transmission_ratio);
}

// Calculates angular acceleration
float calculate_acceleration(float angular_velocity, float prev_angular_velocity, unsigned long dt_ms) {
  if (dt_ms == 0) return 0.0;
  float dt_s = dt_ms / 1000.0;
  return (angular_velocity - prev_angular_velocity) / dt_s;
}

// Determines the gear based on the brake value
int determine_gear(int brake) {
  // Example: adjust logic as needed
  if (brake == 0) return 1;
  else if (brake == 1) return 2;
  else if (brake == 2) return 3;
  else return 0; // Neutral or error
}

void setup() {
  Serial.begin(9600); // UART with STM32
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  prev_time = millis();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  if (Serial.available()) {
    inputData = Serial.readStringUntil('\n');
    inputData.trim();

    // Expects data in format: "angular_velocity,brake"
    int commaIndex = inputData.indexOf(',');
    if (commaIndex > 0) {
      float angular_velocity = inputData.substring(0, commaIndex).toFloat();
      int brake = inputData.substring(commaIndex + 1).toInt();

      unsigned long current_time = millis();
      unsigned long dt = current_time - prev_time;

      float acceleration = calculate_acceleration(angular_velocity, prev_angular_velocity, dt);
      float rpm = calculate_rpm(angular_velocity);
      int gear = determine_gear(brake);

      // Prepare MQTT message
      String mqttMsg = String("{\"angular_velocity\":") + angular_velocity +
                       ",\"brake\":" + brake +
                       ",\"gear\":" + gear +
                       ",\"acceleration\":" + acceleration +
                       ",\"rpm\":" + rpm + "}";

      client.publish("tractor/data", mqttMsg.c_str());

      // Update previous values
      prev_angular_velocity = angular_velocity;
      prev_time = current_time;
    }
  }
}
