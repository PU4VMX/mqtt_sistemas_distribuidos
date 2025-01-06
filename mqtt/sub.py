import paho.mqtt.client as mqtt


class MQTTSubscriberDevice:
    """
    Classe para gerenciar um dispositivo subscriber MQTT.
    """

    def __init__(self, broker="localhost", port=1883, timelive=60, topic="/esp32/analog"):
        """
        Inicializa o dispositivo MQTT Subscriber.

        :param broker: Endereço do broker MQTT.
        :param port: Porta de conexão do broker.
        :param timelive: Tempo de keep-alive para o cliente MQTT.
        :param topic: Tópico para assinatura.
        """
        self.broker = broker
        self.port = port
        self.timelive = timelive
        self.topic = topic
        self.client = mqtt.Client()

        self._configure_client()

    def _configure_client(self):
        """Configura callbacks e conecta ao broker MQTT."""
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def connect(self):
        """Estabelece a conexão com o broker MQTT."""
        try:
            self.client.connect(self.broker, self.port, self.timelive)
        except Exception as e:
            print(f"Erro ao conectar ao broker: {e}")
            raise

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback executado ao conectar com o broker.

        :param client: Instância do cliente MQTT.
        :param userdata: Dados do usuário (não utilizado aqui).
        :param flags: Flags enviadas pelo broker.
        :param rc: Código de resultado da conexão.
        """
        if rc == 0:
            print("Conectado ao broker MQTT com sucesso!")
            self.client.subscribe(self.topic)
            print(f"Assinado no tópico: {self.topic}")
        else:
            print(f"Falha na conexão. Código de retorno: {rc}")

    def on_message(self, client, userdata, msg):
        """
        Callback executado ao receber uma mensagem.

        :param client: Instância do cliente MQTT.
        :param userdata: Dados do usuário (não utilizado aqui).
        :param msg: Mensagem recebida.
        """
        return msg.payload.decode()

    def start(self):
        """
        Inicia o loop principal do cliente MQTT.
        """
        try:
            print("Iniciando o loop MQTT...")
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\nEncerrando o cliente MQTT...")
            self.client.disconnect()


# Exemplo de uso
if __name__ == "__main__":
    sub = MQTTSubscriberDevice(broker="localhost", port=1883, topic="#")
    sub.connect()
    sub.start()
