import paho.mqtt.client as mqtt
import json
import base64

broker_address = "localhost" 
port = 1883  
topic = "test/topic"

def on_message(client, userdata, message):
    payload = str(message.payload.decode('utf-8'))
    data_package = json.loads(payload)
    for key, value in data_package.items():
        value['data'] = base64.b64decode(value['data'])
    print(f"Received message: {data_package} on topic {message.topic}")

client = mqtt.Client("Subscriber")
client.on_message = on_message
client.connect(broker_address, port)
client.subscribe(topic)
client.loop_forever()
