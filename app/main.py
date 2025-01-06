from datetime import datetime
import os
import time
import threading
import uuid
from fastapi import FastAPI, HTTPException
from mqtt.pub import MQTTPublisher
from mqtt.sub import MQTTSubscriberDevice
from app.api import router
from app.database import conexao
from app.sync import Synchronizer


# Constantes de Configuração
INSTANCE = os.getenv("INSTANCE")
INSTANCE_PAIR = os.getenv("INSTANCE_PAIR")
BROKER = os.getenv("MQTT_BROKER", "192.168.2.187")  # IP padrão do broker MQTT
PORT = int(os.getenv("MQTT_PORT", 1883))
SUBSCRIBER_TOPIC = "esp32/umidade"
PUBLISHER_TOPIC = "esp32/atuador"
REMOTE_API_URL = f"http://{INSTANCE_PAIR}:8000/api/"


# Inicializando FastAPI
app = FastAPI()
app.include_router(router, prefix="/api")

# Inicializando serviços

mqtt_publisher = MQTTPublisher(BROKER, PORT, PUBLISHER_TOPIC)
mqtt_subscriber = MQTTSubscriberDevice(BROKER, PORT, 60, SUBSCRIBER_TOPIC)


# Funções
def initialize_mqtt():
    """Inicializa as conexões MQTT e seus callbacks."""
    mqtt_publisher.connect()
    mqtt_subscriber.connect()
    mqtt_subscriber.client.loop_start()
    mqtt_subscriber.client.on_message = handle_incoming_message


# metodo que se a umidade for maior que 80% ele aciona o atuador, se for menor que 80% ele desliga o atuador
def umidade_processada(umidade):
    if umidade > 80:
        mqtt_publisher.publish("true")
        conexao.insert_acionamento(uuid.uuid4(), datetime.now(), True, "automatico")
    else:
        mqtt_publisher.publish("false")
        conexao.insert_acionamento(uuid.uuid4(), datetime.now(), False, "automatico")


def handle_incoming_message(client, userdata, msg):
    """Callback para lidar com mensagens recebidas no MQTT."""
    try:
        print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
        umidade = float(msg.payload.decode())
        umidade_processada(umidade)
        conexao.insert_umidade(uuid.uuid4(), datetime.now(), umidade)
    except ValueError as e:
        print(f"Erro ao processar mensagem MQTT: {e}")



@app.get("/atuador/{estado}")
async def acionar_atuador(estado: str):
    """Endpoint para acionar o atuador com estado 'true' ou 'false'."""
    if estado.lower() not in {"true", "false"}:
        raise HTTPException(
            status_code=400, detail="O estado deve ser 'true' ou 'false'"
        )

    mqtt_publisher.publish(estado)
    conexao.insert_acionamento(
        uuid.uuid4(), datetime.now(), estado.lower() == "true", "manual"
    )
    return {"message": f"Estado do atuador alterado para {estado}"}


def ensure_connection():
    """Verifica periodicamente a conexão MQTT e tenta reconectar se necessário."""
    while True:
        try:
            if not mqtt_publisher.is_connected():
                print("Tentando reconectar ao broker MQTT...")
                mqtt_publisher.connect()
            else:
                print("Conexão com o broker MQTT estável.")
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
        time.sleep(60)


# Inicializando serviços
initialize_mqtt()
threading.Thread(target=ensure_connection, daemon=True).start()
synchronizer = Synchronizer(conexao, REMOTE_API_URL, sync_interval=60)
synchronizer.start()


# Para iniciar o servidor:
# uvicorn app.main:app --reload
