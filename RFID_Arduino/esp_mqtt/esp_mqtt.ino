#include <WiFi.h>
#include <PubSubClient.h>

const char* ssid = "THE FACTORY - ROUTER 2";
const char* password = "legofactory";
const char* mqtt_server = "192.168.0.50";

WiFiClient wifiClient;
PubSubClient client(wifiClient);

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
  }
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}

void callback(char* topic, byte* payload, unsigned int length) {
  // handle incoming messages from subscribed topics
}

void reconnect() {
  while (!client.connected()) {
    if (client.connect("esp32_client")) {
      // publish Hello
      send_message();
      // subscribe to MQTT topics
      client.subscribe("test_topic");
    } else {
      delay(5000);
    }
  }
}

void send_message() {
  // publish a message to an MQTT topic
  client.publish("test_topic", "Hello from ESP32!");
  Serial.println("mqtt verification test");
}
