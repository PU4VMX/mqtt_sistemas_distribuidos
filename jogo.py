import turtle
import time
import threading
import random
from pub import MQTTPublisher
from sub import MQTTClientSubscriber


class MQTTController:
    def __init__(self, player_id, broker="localhost", port=1883, timelive=60):
        self.player_id = player_id  # ID do jogador
        self.publisher = MQTTPublisher(client_id=self.player_id, broker=broker, port=port)
        self.subscriber = MQTTClientSubscriber(broker=broker, port=port, timelive=timelive)
        self.subscriber.client.on_message = self.on_message_callback
        self.players = {}  # Dicionário para armazenar outros jogadores

    def connect(self):
        self.publisher.connect()
        self.subscriber.start_thread()

    def publish_direction(self, direction):
        self.publisher.publish_messages(topic="/data", direction=direction)

    def publish_position(self, x, y):
        self.publisher.publish_messages(topic="/data", position=f"{self.player_id},{x},{y}")

    def close_connection(self):
        self.publisher.publish_messages(topic="/data", id=0, direction="stop")

    def on_message_callback(self, client, userdata, message):
        print(f"Mensagem recebida: {message.payload.decode()}")
        parts = message.payload.decode().split(",")

        # Verifica se a mensagem contém a posição de um jogador
        if len(parts) == 3:  # ID, X, Y
            player_id, x, y = parts
            if player_id not in self.players:
                self.players[player_id] = turtle.Turtle()  # Cria uma nova tartaruga para o jogador
                self.players[player_id].speed(0)
                self.players[player_id].shape("circle")
                self.players[player_id].color("blue")  # Define a cor para os outros jogadores
                self.players[player_id].penup()

            # Atualiza a posição do jogador
            self.players[player_id].updade

    def listen(self):
        """Inicia o loop de escuta do MQTT."""
        self.subscriber.client.loop_forever()  # Mantém o cliente em escuta ativa


class Player:
    def __init__(self, color):
        self.head = turtle.Turtle()
        self.head.speed(0)
        self.head.shape("circle")
        self.head.color(color)  # Define a cor do jogador
        self.head.penup()
        self.head.goto(0, 0)
        self.head.direction = "stop"

    def update_direction(self, direction):
        if direction == "up" and self.head.direction != "down":
            self.head.direction = "up"
        elif direction == "down" and self.head.direction != "up":
            self.head.direction = "down"
        elif direction == "left" and self.head.direction != "right":
            self.head.direction = "left"
        elif direction == "right" and self.head.direction != "left":
            self.head.direction = "right"
        elif direction == "stop":
            self.head.direction = "stop"

    def move(self, wn, delay):
        if self.head.direction == "up":
            self.head.sety(self.head.ycor() + 2)
        elif self.head.direction == "down":
            self.head.sety(self.head.ycor() - 2)
        elif self.head.direction == "left":
            self.head.setx(self.head.xcor() - 2)
        elif self.head.direction == "right":
            self.head.setx(self.head.xcor() + 2)

        if abs(self.head.xcor()) > wn.window_width() / 2 or abs(self.head.ycor()) > wn.window_height() / 2:
            self.head.goto(0, 0)
            self.head.direction = "stop"

        wn.update()
        time.sleep(delay)


class GameController:
    def __init__(self, player_id, color, delay=0.01):
        self.delay = delay
        self.wn = turtle.Screen()
        self.wn.title("Move Game by @Garrocho")
        self.wn.bgcolor("green")
        self.wn.setup(width=1.0, height=1.0)
        self.wn.tracer(0)
        self.player = Player(color)  # Passa a cor do jogador
        self.mqtt_controller = MQTTController(player_id)  # Passa o ID do jogador

    def setup_controls(self):
        self.wn.listen()
        self.wn.onkeypress(lambda: self.mqtt_controller.publish_direction("up"), "w")
        self.wn.onkeypress(lambda: self.mqtt_controller.publish_direction("down"), "s")
        self.wn.onkeypress(lambda: self.mqtt_controller.publish_direction("left"), "a")
        self.wn.onkeypress(lambda: self.mqtt_controller.publish_direction("right"), "d")
        self.wn.onkeypress(self.close_game, "Escape")

    def close_game(self):
        self.mqtt_controller.close_connection()
        self.wn.bye()

    def start_game(self):
        self.mqtt_controller.connect()
        self.setup_controls()

        listen_thread = threading.Thread(target=self.mqtt_controller.listen)
        listen_thread.daemon = True
        listen_thread.start()

        move_thread = threading.Thread(target=self.run_game_loop)
        move_thread.daemon = True
        move_thread.start()

        self.wn.mainloop()

    def run_game_loop(self):
        while True:
            x, y = self.player.move(self.wn, self.delay)
            # Publica a posição do jogador
            self.mqtt_controller.publish_position(x, y)


if __name__ == "__main__":
    player_id = str(random.randint(1, 100))  # Gera um ID de jogador aleatório
    colors = ["blue", "red", "yellow", "orange", "purple", "pink"]
    color = random.choice(colors)  # Escolhe uma cor aleatória para o jogador
    game = GameController(player_id, color)  # Passa o ID e a cor do jogador
    game.start_game()
