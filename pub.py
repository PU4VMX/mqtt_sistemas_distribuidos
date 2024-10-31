import paho.mqtt.client as mqtt

class MQTTPublisher:
    def __init__(self, client_id="admin", broker="localhost", port=1883):
        self.client_id = client_id
        self.broker = broker
        self.port = port
        self.client = mqtt.Client(client_id=self.client_id, protocol=mqtt.MQTTv311)
        
        # Configura o callback de publicação
        self.client.on_publish = self.on_publish

    def connect(self):
        """Conecta ao broker MQTT."""
        self.client.connect(self.broker, self.port)

    def publish_messages(self, topic="/data", direction="stop", color="blue"):
        """Publica mensagens no broker MQTT."""
        self.client.publish(topic, f"{self.client_id},{direction}, {color}")

    def on_publish(self, client, userdata, mid):
        """Callback executado ao publicar uma mensagem."""
        print(f"Message {mid} published.")
        