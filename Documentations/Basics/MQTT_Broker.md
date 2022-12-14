# MQTT

### Definitions

- MQTT: light protocol to send and receives message
- Broker: The “place” where the messages are managed
- Mosquitto: Create a broker in your computer / device
- Topic: Name of the a specific category to cluster the messages
- Publish: Send message to a specific topic
- Subscribe: Receives a message from a specific topic

### Implementations of Mosquitto / Broker

Follow the instructions of the website: 

[How to Install The Mosquitto MQTT Broker- Windows and Linux](http://www.steves-internet-guide.com/install-mosquitto-broker/)

1. Download the zip folder:

[http://www.steves-internet-guide.com/download/64-bit-mosquitto-v-1-6-9-for-windows/](http://www.steves-internet-guide.com/download/64-bit-mosquitto-v-1-6-9-for-windows/)

1. Unzip the folder in somewhere (like Desktop) and rename the folder as you want (like “mosquitto”)
2. Open your Command Prompt, open the folder and run

```arduino
cd desktop\mosquitto
mosquitto -v
```

1. You should see something like that:

```arduino
1664365630: mosquitto version 1.6.9 starting
1664365630: Using default config.
1664365630: Opening ipv6 listen socket on port 1883.
1664365630: Opening ipv4 listen socket on port 1883.
```

### Finding your IP Adress

You need the IP adress of the broker (the PC running Mosquitto), for that you can follow the steps:

1. Open you Command Prompt and type:

```arduino
ipconfig
```

1. You should see something like this (your IP Adress in highlighted)

![image](https://user-images.githubusercontent.com/72768576/207636778-bf5cd314-5dab-4cf5-8ba8-6dd77e26ab89.png)

⚠️ Warning: 

To create the communication between 2 or more devices, all the devices need to be connected to the same network, i. e., if the broker is connected to the local network (lego factory) than all the other devices (stations or PCs) need to be in the same local network!

### Publishing

To publish a message is really straight forward, just follow the steps:

1. Import the libraries (make sure that you have install paho.mqtt library)
2. Set the message (call payload) as a dictionary

```python
#--- Payload (message to be send to the topics)
payload = {
    "time" : 4,
    "workpieces" : 50,
    "free" : "no"
}
```

1. Create the clien and make the connection:

```python
#--- Connection to the Client
client = mqtt.Client()
client.connect("192.168.0.104", 1883, 60)
#IP adress of the broker, 1883 and 60 is the default to a Mosquitto Broker
```

As you can see, first we create an object call Client from the class mqqt.client. After this we make the connection with the Broker. It’s important to put the correct Broker’s IP Adress. The other parameters are default for Mosquitto Broker, don’t change it. 

1. Finally, publish the message:

```python
#--- Publish a message
client.publish(topic = "activity", payload= json.dumps(payload))
```

First you need to tell what are the topic of this message and than specify the message itself. It’s important to convert any message format to the json format, that’s why we use method json.dumps(<message>).

### Subscribing

1. Import the libraries (make sure that you have install paho.mqtt library)
2. Definition of functions to handle the subscription and receiving messages
    1. “on_connect”: It’s a function that after the connection create the subscripition in different topics
    2. “on_message”: It’s a functions to deal with the new messages received in different topics. With this function you can treat the received payload as you want.
    
    ```python
    # defining topics to subscribe
    
    def on_connect(client, userdata, flags, rc):
      print("Connected with result code "+str(rc))
      client.subscribe(topic="activity")
    
    # manipulation of subscribed message data
    def on_message(client, userdata, msg):
        # define global variables
        #print(msg.payload) 
        print(str(msg.payload.decode("utf-8")))     # to print the message string
        json_value = json.loads(msg.payload.decode())  #converting message string to python dictionary
        print("time",json_value['time'])   # calling individual data in the json dictionary
        print(json_value)
    ```
    
3. Create the object and make the connection with the Brokers, as it was explained before :

```python
client = mqtt.Client()
client.connect("192.168.0.104",1883,60,) # verify the IP address before connect
```

1. Define how the client will deal with the connection and with new messages (just passing our functions)

```python
client.on_connect = on_connect
client.on_message = on_message
```

1. Start a loop that will by default verify if there are new messages arriving from the Broker. In the middle of this Loop we could something if the received messaged, but here we just stay forever receiving payloads. 

```python
client.loop_start()
condition = True

while condition:        # the system stays connected as long as the condition is "True"
    sleep(1)
    
client.loop_stop()    
client.disconnect()
```

## MQTT client for Linux Ubuntu

MQTT box interface is available only as web-app in google chrome. Alternate app similar to MQTTX can be installed directly from snap store in Ubuntu.

Snap store can be opened from Linux Terminal by running following command.
