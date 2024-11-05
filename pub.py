import json
import paho.mqtt.client as mqtt

# Classe para o dispositivo publisher MQTT
class MQTTPublisherDevice:
    def __init__(self, broker="localhost", port=1883, client_id="admin", id=0):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id)
        self.client.on_publish = self.on_publish
        self.client.connect(self.broker, self.port)
        self.id = id

    def on_publish(self, client, userdata, result):
        print("Dado publicado com sucesso")

    def publish_data(self, topic="/data", x=0, y=0):
        data = json.dumps({"id": self.id, "x": x, "y": y})
        self.client.publish(topic, data)

    def start(self):
        self.client.loop_start()