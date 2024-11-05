import paho.mqtt.client as mqtt

# Classe para o dispositivo subscriber MQTT
class MQTTSubscriberDevice:
    def __init__(self, broker="localhost", port=1883, timelive=60):
        self.broker = broker
        self.port = port
        self.timelive = timelive
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        print("Conectado com código de resultado " + str(rc))
        client.subscribe("/data")

    def on_message(self, client, userdata, msg):
        print("Mensagem recebida: ", msg.payload.decode())

    def set_on_message_callback(self, callback):
        self.client.on_message = callback

    def start(self):
        self.client.connect(self.broker, self.port, self.timelive)
        self.client.loop_start()