from sqlalchemy import create_engine, text, inspect
from src.config.settings import settings

class DatabaseClient:
    def __init__(self):
        self.oltp_engine = create_engine(settings.OLTP_URL, pool_pre_ping=True)
        self.olap_engine = create_engine(settings.OLAP_URL, pool_pre_ping=True)

    def get_oltp_connection(self):
        return self.oltp_engine.connect()

    def get_olap_connection(self):
        return self.olap_engine.connect()

    def get_olap_tables(self):
        inspector = inspect(self.olap_engine)
        return inspector.get_table_names()

    def get_oltp_tables(self):
        inspector = inspect(self.oltp_engine)
        return inspector.get_table_names()

    def get_source_columns(self, table_name: str):
        inspector = inspect(self.oltp_engine)
        if "." in table_name:
            schema, tbl = table_name.split(".", 1)
            cols = inspector.get_columns(tbl, schema=schema)
        else:
            cols = inspector.get_columns(table_name)
        return [{"name": c["name"], "type": str(c["type"])} for c in cols]

    def get_target_columns(self, table_name: str):
        inspector = inspect(self.olap_engine)
        if "." in table_name:
            schema, tbl = table_name.split(".", 1)
            cols = inspector.get_columns(tbl, schema=schema)
        else:
            cols = inspector.get_columns(table_name)
        return [{"name": c["name"], "type": str(c["type"])} for c in cols]