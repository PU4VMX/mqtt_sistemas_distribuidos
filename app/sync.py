import time
import threading

from fastapi import requests


class MultiSynchronizer:
    def __init__(self, local_db, remote_instances, sync_interval=60):
        """
        Inicializa o sincronizador multilateral.

        :param local_db: Instância da classe Database para o banco local.
        :param remote_instances: Lista de URLs das APIs remotas.
        :param sync_interval: Intervalo de sincronização em segundos.
        """
        self.local_db = local_db
        self.remote_instances = remote_instances
        self.sync_interval = sync_interval

    def sync_with_instance(self, remote_api_url):
        """
        Sincroniza os dados com uma instância remota específica.
        """
        try:
            print(f"Sincronizando com a instância {remote_api_url}...")

            # Sincronizar tabela umidade
            self.sync_table(
                remote_api_url, "umidade", 
                ["id", "data", "valor", "last_updated"], 
                self.local_db.get_umidade()
            )

            # Sincronizar tabela acionamentos
            self.sync_table(
                remote_api_url, "acionamentos", 
                ["id", "timestamp", "estado", "gatilho", "last_updated"], 
                self.local_db.get_acionamentos()
            )

            print(f"Sincronização com {remote_api_url} concluída.")
        except Exception as e:
            print(f"Erro ao sincronizar com {remote_api_url}: {e}")

    def sync_table(self, remote_api_url, table_name, fields, local_data):
        """
        Sincroniza uma tabela específica entre o banco local e remoto.

        :param remote_api_url: URL da instância remota.
        :param table_name: Nome da tabela.
        :param fields: Lista dos campos da tabela.
        :param local_data: Dados locais para sincronizar.
        """
        # Buscar dados remotos
        remote_data = self.fetch_remote_data(remote_api_url, table_name)

        # Normalizar para comparação
        remote_data_dict = {row["id"]: row for row in remote_data}
        local_data_dict = {row[0]: dict(zip(fields, row)) for row in local_data}

        # Verificar atualizações e sincronizar
        for id, local_row in local_data_dict.items():
            remote_row = remote_data_dict.get(id)

            if not remote_row or local_row["last_updated"] > remote_row["last_updated"]:
                # Atualizar no remoto
                self.insert_or_update_remote_data(remote_api_url, table_name, local_row)
            elif remote_row["last_updated"] > local_row["last_updated"]:
                # Atualizar no local
                self.update_local_data(table_name, remote_row)

    def fetch_remote_data(self, remote_api_url, table_name):
        """Busca os dados da tabela no banco remoto via API."""
        response = requests.get(f"{remote_api_url}/{table_name}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(
                f"Erro ao buscar dados remotos: {response.status_code}, {response.text}"
            )

    def insert_or_update_remote_data(self, remote_api_url, table_name, data):
        """Insere ou atualiza dados no banco remoto via API."""
        response = requests.post(f"{remote_api_url}/{table_name}", json=data)
        if response.status_code not in {200, 201}:
            raise Exception(
                f"Erro ao inserir/atualizar dados no banco remoto: {response.status_code}, {response.text}"
            )

    def update_local_data(self, table_name, data):
        """Atualiza dados no banco local."""
        if table_name == "umidade":
            self.local_db.insert_umidade(
                data["id"], data["data"], data["valor"], data["last_updated"]
            )
        elif table_name == "acionamentos":
            self.local_db.insert_acionamento(
                data["id"], data["timestamp"], data["estado"], 
                data["gatilho"], data["last_updated"]
            )

    def start(self):
        """Inicia o processo de sincronização em threads separadas."""
        def sync_cycle():
            while True:
                for remote_instance in self.remote_instances:
                    self.sync_with_instance(remote_instance)
                time.sleep(self.sync_interval)

        threading.Thread(target=sync_cycle, daemon=True).start()
