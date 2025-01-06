from cassandra.cluster import Cluster


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
            "id UUID PRIMARY KEY,"
            "data TIMESTAMP,"
            "valor FLOAT"
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


    def insert_acionamento(self, id, timestamp, estado):
        self.session.execute(
            "INSERT INTO acionamentos (id, timestamp, estado, gatilho) VALUES (%s, %s, %s, %s);",
            (id, timestamp, estado, "API"),
        )


    def insert_umidade(self, id, data, valor):
        self.session.execute(
            "INSERT INTO umidade (id, data, valor) VALUES (%s, %s, %s);",
            (id, data, valor),
        )


    def get_umidade(self):
        result = self.session.execute("SELECT * FROM umidade;")
        return result


    def get_acionamentos(self):
        result = self.session.execute("SELECT * FROM acionamentos;")
        return result


    def close(self):
        self.cluster.shutdown()
