#--- Import
import json
import paho.mqtt.client as mqtt

#--- Payload (message to be send to the topics)
payload = {
    "time" : 4,
    "workpieces" : 50,
    "free" : "no"
}

#--- Connection to the Client
client = mqtt.Client()
client.connect("192.168.0.104", 1883, 60)
#IP adress of the broker, 1883 and 60 is the default to a Mosquitto Broker

#--- Publish a message
client.publish(topic = "activity", payload= json.dumps(payload))



