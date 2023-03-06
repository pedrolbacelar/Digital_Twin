
import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
last_id = 000000

try:
    def on_connect(client, userdata, flags, rc):
        print("Connected with result code "+str(rc))

    client = mqtt.Client()
    client.connect("192.168.2.70",1883,60) # verify the IP address before connect
    client.on_connect = on_connect
    client.on_message = on_message

    while True:
        id, text = reader.read()
        if id != last_id:
            print("id : ",id)
            payload ={"machine_id" : "1", "part_id":id}
            client.publish(topic = "part_id", payload= json.dumps(payload))
            last_id = id
        else:
            print("same part detected again")
finally:
    GPIO.cleanup()