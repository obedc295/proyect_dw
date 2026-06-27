from sqlalchemy import create_engine, text
from src.config.settings import settings

class DatabaseClient:
    def __init__(self):
        # pool_pre_ping=True obliga a verificar que la conexión esté viva antes de usarla,
        # lo que evita que la segunda conexión falle por temas de sincronización temporal.
        self._oltp_engine = create_engine(settings.OLTP_URL, pool_pre_ping=True)
        self._olap_engine = create_engine(settings.OLAP_URL, pool_pre_ping=True)

    def get_oltp_connection(self):
        return self._oltp_engine.connect()

    def get_olap_connection(self):
        return self._olap_engine.connect()