import threading
import paho.mqtt.client as mqtt

class MQTTClientSubscriber:
    def __init__(self, broker="localhost", port=1883, timelive=60):
        self.broker = broker
        self.port = port
        self.timelive = timelive
        self.client = mqtt.Client()
        
        # Configura os callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        """Conecta ao broker MQTT."""
        self.client.connect(self.broker, self.port, self.timelive)

    def on_connect(self, client, userdata, flags, rc):
        """Callback executado ao conectar com sucesso ao broker."""
        print("Connected with result code " + str(rc))
        client.subscribe("/data")

    def on_message(self, client, userdata, message):
        """Callback executado ao receber uma mensagem."""
        print("Message received: " + message.payload.decode())

    def start(self):
        """Inicia o loop de escuta do cliente MQTT."""
        self.connect()
        self.client.loop_forever()

    def start_thread(self):
        """Inicia o loop de escuta do cliente MQTT em uma thread separada."""
        mqtt_thread = threading.Thread(target=self.start)
        mqtt_thread.start()

