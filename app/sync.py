import time
import threading

from fastapi import requests

class Synchronizer:
    def __init__(self, local_db, remote_api_url, sync_interval=60):
        """
        Inicializa o sincronizador.

        :param local_db: Instância da classe Database para o banco local.
        :param remote_api_url: URL base da API remota (FastAPI2).
        :param sync_interval: Intervalo de sincronização em segundos.
        """
        self.local_db = local_db
        self.remote_api_url = remote_api_url
        self.sync_interval = sync_interval

    def sync_data(self):
        """Realiza a sincronização entre o banco local e o remoto."""
        while True:
            try:
                print("Sincronizando dados...")

                # Sincronizar umidade
                self.sync_table(
                    "umidade", 
                    ["id", "data", "valor"], 
                    self.local_db.get_umidade()
                )

                # Sincronizar acionamentos
                self.sync_table(
                    "acionamentos",
                    ["id", "timestamp", "estado", "gatilho"],
                    self.local_db.get_acionamentos()
                )
                
                print("Sincronização concluída.")
            except Exception as e:
                print(f"Erro durante a sincronização: {e}")
            time.sleep(self.sync_interval)

    def sync_table(self, table_name, fields, local_data):
        """
        Sincroniza uma tabela específica entre os bancos.

        :param table_name: Nome da tabela.
        :param fields: Lista dos campos da tabela.
        :param local_data: Dados locais para sincronizar.
        """
        # Obter os dados do banco remoto
        remote_data = self.fetch_remote_data(table_name)

        # Normalizar dados para comparação
        remote_data_set = {tuple(row.values()) for row in remote_data}
        local_data_set = {tuple(row) for row in local_data}

        # Identificar registros ausentes
        missing_in_remote = local_data_set - remote_data_set

        # Inserir registros ausentes no banco remoto
        for row in missing_in_remote:
            payload = dict(zip(fields, row))
            self.insert_remote_data(table_name, payload)

    def fetch_remote_data(self, table_name):
        """Busca os dados de uma tabela no banco remoto via API."""
        response = requests.get(f"{self.remote_api_url}/{table_name}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Erro ao buscar dados remotos: {response.status_code}, {response.text}"
            )

    def insert_remote_data(self, table_name, data):
        """Insere dados no banco remoto via API."""
        response = requests.post(f"{self.remote_api_url}/{table_name}", json=data)
        if response.status_code not in {200, 201}:
            raise Exception(
                f"Erro ao inserir dados no banco remoto: {response.status_code}, {response.text}"
            )

    def start(self):
        """Inicia o processo de sincronização em uma thread separada."""
        threading.Thread(target=self.sync_data, daemon=True).start()
