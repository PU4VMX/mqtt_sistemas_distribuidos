from datetime import datetime
import os
import time
import threading
import uuid
from fastapi import FastAPI, HTTPException
from app.database import Database
from mqtt.pub import MQTTPublisher
from mqtt.sub import MQTTSubscriberDevice
from app.api import router

# Constantes de Configuração
INSTANCE = os.getenv("INSTANCE")
BROKER = os.getenv("MQTT_BROKER", "192.168.2.187")  # IP padrão do broker MQTT
PORT = int(os.getenv("MQTT_PORT", 1883))
SUBSCRIBER_TOPIC = "esp32/umidade"
PUBLISHER_TOPIC = "esp32/atuador"
CLUSTERS = os.getenv("DB_CLUSTERS", "172.17.0.2").split(",")

# Inicializando FastAPI
app = FastAPI()
app.include_router(router, prefix="/api")

# Inicializando serviços
database = Database(CLUSTERS)
mqtt_publisher = MQTTPublisher(BROKER, PORT, PUBLISHER_TOPIC)
mqtt_subscriber = MQTTSubscriberDevice(BROKER, PORT, 60, SUBSCRIBER_TOPIC)


# Funções
def initialize_mqtt():
    """Inicializa as conexões MQTT e seus callbacks."""
    mqtt_publisher.connect()
    mqtt_subscriber.connect()
    mqtt_subscriber.client.loop_start()
    mqtt_subscriber.client.on_message = handle_incoming_message


def handle_incoming_message(client, userdata, msg):
    """Callback para lidar com mensagens recebidas no MQTT."""
    try:
        print(f"Mensagem recebida no tópico {msg.topic}: {msg.payload.decode()}")
        umidade = float(msg.payload.decode())
        database.insert_umidade(uuid.uuid4(), datetime.now(), umidade)
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

# Para iniciar o servidor:
# uvicorn app.main:app --reload
