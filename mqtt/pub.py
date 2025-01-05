import paho.mqtt.client as mqtt

class MQTTPublisher:
    def __init__(self, broker, port, topic):
        self.broker = broker
        self.port = port
        self.topic = topic
        self.client = mqtt.Client()

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, keepalive=60)
            print(f"Conectado ao broker MQTT {self.broker}:{self.port}")
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
            raise

    def publish(self, message):
        try:
            self.client.publish(self.topic, message)
            print(f"Mensagem '{message}' publicada no tópico '{self.topic}'")
        except Exception as e:
            print(f"Erro ao publicar no MQTT: {e}")

    def disconnect(self):
        self.client.disconnect()
        print("Desconectado do broker MQTT")

    def is_connected(self):
        return self.client.is_connected()

def main():
    # Configurações do Broker MQTT
    broker = "192.168.2.187"  # Substitua pelo IP do seu broker MQTT
    port = 1883
    topic = "esp32/atuador"

    mqtt_publisher = MQTTPublisher(broker, port, topic)

    try:
        mqtt_publisher.connect()

        while True:
            print("Digite 'true' para ligar o LED ou 'false' para desligar (ou 'sair' para encerrar):")
            entrada = input("Mensagem: ").strip().lower()

            if entrada == "sair":
                print("Encerrando o programa.")
                break
            elif entrada in ["true", "false"]:
                mqtt_publisher.publish(entrada)
            else:
                print("Entrada inválida. Digite 'true', 'false' ou 'sair'.")
    finally:
        mqtt_publisher.disconnect()

if __name__ == "__main__":
    main()
