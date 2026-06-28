import pandas as pd 
from sqlalchemy import text, inspect

class DataExtractor: 
    def __init__(self, db_client):
        self.db = db_client


    def extract_by_table(self, table_name: str): 
        query = f"SELECT * FROM {table_name}"
        
        with self.db.get_oltp_connection() as conn: 
            df = pd.read_sql(text(query), conn)
            return df
        

    def extract_by_query(self, sql_query: str):
        with self.db.get_oltp_connection() as conn: 
            df = pd.read_sql(text(sql_query), conn)
        return df

    def extract_tables(self):
        inspector = inspect(self.db)
        return inspector.get_table_names()