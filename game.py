import paho.mqtt.client as mqtt
import random
import threading
import turtle
import time
import json

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


# Classe principal do jogo
class Game:
    def __init__(self, mqtt_sub, mqtt_pub):
        self.delay = 0.01
        self.score = 0
        self.high_score = 0
        self.mqtt_sub = mqtt_sub
        self.mqtt_pub = mqtt_pub
        self.players = {}
        self.colors = ["red", "blue", "yellow", "purple", "orange", "pink", "brown", "black"]

        # Configuração da tela
        self.wn = turtle.Screen()
        self.wn.title("Move Game by @Garrocho")
        self.wn.bgcolor("green")
        self.wn.setup(width=1.0, height=1.0, startx=None, starty=None)
        self.wn.tracer(0)

        # Criar o jogador local com uma cor padronizada
        self.player_id = mqtt_pub.id
        self.create_player(self.player_id)

        # Configuração dos controles de movimento
        self.wn.listen()
        self.wn.onkeypress(self.go_up, "w")
        self.wn.onkeypress(self.go_down, "s")
        self.wn.onkeypress(self.go_left, "a")
        self.wn.onkeypress(self.go_right, "d")
        self.wn.onkeypress(self.close, "Escape")

    def get_color_for_player(self, player_id):
        """Seleciona uma cor padronizada para cada jogador com base no ID"""
        index = hash(player_id) % len(self.colors)
        return self.colors[index]

    def create_player(self, player_id):
        """Cria uma bolinha para o jogador especificado pelo ID"""
        if player_id not in self.players:
            color = self.get_color_for_player(player_id)
            player_turtle = turtle.Turtle()
            player_turtle.speed(0)
            player_turtle.shape("circle")
            player_turtle.color(color)
            player_turtle.penup()
            player_turtle.goto(0, 0)
            self.players[player_id] = player_turtle

    def update_position(self):
        """Atualiza a posição do jogador local e publica os dados"""
        x = self.players[self.player_id].xcor()
        y = self.players[self.player_id].ycor()
        self.mqtt_pub.publish_data(x=x, y=y)

    def go_up(self):
        y = self.players[self.player_id].ycor()
        self.players[self.player_id].sety(y + 10)
        self.update_position()

    def go_down(self):
        y = self.players[self.player_id].ycor()
        self.players[self.player_id].sety(y - 10) 
        self.update_position()

    def go_left(self):
        x = self.players[self.player_id].xcor()
        self.players[self.player_id].setx(x - 10)
        self.update_position()

    def go_right(self):
        x = self.players[self.player_id].xcor()
        self.players[self.player_id].setx(x + 10)
        self.update_position()

    def close(self):
        self.wn.bye()

    def on_message(self, client, userdata, msg):
        """Callback para processar mensagens MQTT recebidas"""
        data = json.loads(msg.payload.decode())
        player_id = data["id"]
        x = data["x"]
        y = data["y"]
        
        # Cria o jogador caso não exista ainda
        self.create_player(player_id)
        
        # Atualiza a posição do jogador
        self.players[player_id].goto(x, y)

    def run(self):
        """Loop principal do jogo"""
        while True:
            self.wn.update()
            time.sleep(self.delay)

    def start(self):
        """Inicia o jogo e a escuta de mensagens MQTT"""
        self.mqtt_sub.set_on_message_callback(self.on_message)
        threading.Thread(target=self.run).start()


if __name__ == "__main__":
    # Instancia o subscriber e publisher MQTT
    mqtt_sub = MQTTSubscriberDevice()
    mqtt_pub = MQTTPublisherDevice(id=random.randint(1, 1000))

    # Inicia os dispositivos MQTT em threads separadas
    threading.Thread(target=mqtt_sub.start).start()
    threading.Thread(target=mqtt_pub.start).start()

    # Aguarda a conexão MQTT antes de iniciar o jogo
    time.sleep(2)

    # Inicia o jogo
    game = Game(mqtt_sub, mqtt_pub)
    game.start()
    turtle.done()
