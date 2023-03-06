#--- read rfid tag and send the part id
#--- part id is different from the tag id which is unique.
#--- station 1 RFID reader assigns part_id to the tag (reader.write())


import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

reader = SimpleMFRC522()
last_id = 000000
part_id = 1
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
            print("id : ",id, "part_id : ", part_id)
            reader.write(part_id)   # write the part_id to the tag.
            payload ={"machine_id" : "1", "part_id":part_id}
            client.publish(topic = "part_id", payload= json.dumps(payload))
            last_id = id
            part_id += 1
        else:
            print("same part detected again")
finally:
    GPIO.cleanup()