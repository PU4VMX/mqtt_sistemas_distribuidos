import os
from cassandra.cluster import Cluster


CLUSTERS = os.getenv("DB_CLUSTERS").split(",")

class Database:
    def __init__(self, clusters):
        self.cluster = Cluster(clusters, port=9042)
        self.session = self.cluster.connect()
        self.session.execute(
            "CREATE KEYSPACE IF NOT EXISTS iot WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };"
        )
        self.session.set_keyspace("iot")
        self.session.execute(
            "CREATE TABLE IF NOT EXISTS umidade ("
            "id UUID,"
            "data TIMESTAMP,"
            "valor FLOAT,"
            "PRIMARY KEY (data, id)"
            ");"
        )
        self.session.execute(
            "CREATE TABLE IF NOT EXISTS acionamentos ("
            "id UUID PRIMARY KEY,"
            "timestamp TIMESTAMP,"
            "estado BOOLEAN,"
            "gatilho TEXT"
            ");"
        )
        # Criando índices para consultas por data e estado
        self.session.execute("CREATE INDEX IF NOT EXISTS idx_umidade_data ON umidade (data);")
        self.session.execute("CREATE INDEX IF NOT EXISTS idx_acionamentos_estado ON acionamentos (estado);")
        self.insert_acionamento_stmt = self.session.prepare(
            "INSERT INTO acionamentos (id, timestamp, estado, gatilho) VALUES (?, ?, ?, ?);"
        )
        self.insert_umidade_stmt = self.session.prepare(
            "INSERT INTO umidade (id, data, valor) VALUES (?, ?, ?);"
        )

    def insert_acionamento(self, id, timestamp, estado, gatilho):
        self.session.execute(self.insert_acionamento_stmt, (id, timestamp, estado, gatilho))

    def insert_umidade(self, id, data, valor):
        self.session.execute(self.insert_umidade_stmt, (id, data, valor))

    def get_umidade(self):
        result = self.session.execute("SELECT id, data, valor FROM umidade LIMIT 100;")
        return result

    def get_acionamentos(self):
        result = self.session.execute("SELECT id, timestamp, estado, gatilho FROM acionamentos LIMIT 100;")
        return result

    def close(self):
        self.cluster.shutdown()

conexao = Database(CLUSTERS)
