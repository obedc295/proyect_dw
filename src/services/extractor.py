import pandas as pd 
from sqlalchemy import text, inspect

class DataExtractor: 
    def __init__(self, db_client):
        self.db = db_client


    def extract_by_table(self, table_name: str, columns: list[str] | None = None, limit: int | None = None):
        cols = ", ".join(columns) if columns else "*"
        if limit:
            query = f"SELECT TOP {limit} {cols} FROM {table_name}"
        else:
            query = f"SELECT {cols} FROM {table_name}"

        with self.db.get_oltp_connection() as conn:
            df = pd.read_sql(text(query), conn)
            return df
        

    def extract_by_query(self, sql_query: str, limit: int | None = None):
        if limit:
            query = f"SELECT TOP {limit} * FROM ({sql_query}) AS _preview"
        else:
            query = sql_query
        with self.db.get_oltp_connection() as conn: 
            df = pd.read_sql(text(query), conn)
        return df

    def extract_tables(self):
        inspector = inspect(self.db.oltp_engine)
        system_schemas = {
            "sys", "INFORMATION_SCHEMA", "guest",
            "db_owner", "db_accessadmin", "db_securityadmin",
            "db_ddladmin", "db_backupoperator", "db_datareader",
            "db_datawriter", "db_denydatareader", "db_denydatawriter",
        }
        tables = []
        for schema in inspector.get_schema_names():
            if schema.lower() in system_schemas:
                continue
            for table in inspector.get_table_names(schema=schema):
                tables.append(f"{schema}.{table}")
        return tables