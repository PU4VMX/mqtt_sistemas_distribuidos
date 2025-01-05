import os
import time
import threading
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from mqtt.pub import MQTTPublisher
from mqtt.sub import MQTTSubscriberDevice

INSTANCE = os.getenv('INSTANCE')

# Definindo o caminho do arquivo HTML
HTML_PATH = os.path.join(os.path.dirname(__file__), 'index.html')

# Configurações do broker MQTT
BROKER = "192.168.2.187"  # Substitua pelo IP do seu broker MQTT
PORT = 1883

# Inicializando o FastAPI
app = FastAPI()

# Inicializando o publisher MQTT
mqtt_publisher = MQTTPublisher(BROKER, PORT, 'esp32/atuador')
mqtt_publisher.connect()

# Inicializando o subscriber MQTT
mqtt_subscriber = MQTTSubscriberDevice(BROKER, PORT, 60, 'esp32/umidade')
mqtt_subscriber.connect()
mqtt_subscriber.client.loop_start()

@app.get("/")
async def get_html():
    return FileResponse(HTML_PATH)

@app.get("/atuador/{estado}")
async def acionar_atuador(estado: str):
    """Função para acionar o atuador com estado 'true' ou 'false'."""
    if estado.lower() not in ["true", "false"]:
        raise HTTPException(status_code=400, detail="O estado deve ser 'true' ou 'false'")
    
    # Publica o estado no MQTT
    mqtt_publisher.publish(estado)
    return {"message": f"Estado do atuador alterado para {estado}"}

def ensure_connection():
    """Função para garantir que a conexão MQTT esteja estável."""
    while True:
        try:
            if not mqtt_publisher.is_connected():
                print("Tentando reconectar ao broker MQTT...")
                mqtt_publisher.connect()
            else:
                print("Conexão com o broker MQTT estável.")
            time.sleep(60)  # Verifica a conexão a cada 60 segundos
        except Exception as e:
            print(f"Erro ao conectar ao broker MQTT: {e}")
            time.sleep(60)  # Espera 60 segundos antes de tentar reconectar

# Inicia a verificação de conexão em um thread separado
threading.Thread(target=ensure_connection, daemon=True).start()

# Iniciar o servidor com o comando:
# uvicorn app.main:app --reload
