from sqlalchemy import text
from src.infrastructure.db_client import DatabaseClient
import pandas as pd


class DataLoader:
    def __init__(self, db_client: DatabaseClient):
        self.db_client = db_client

    def load_incremental(self, df_transformer, table_name:str, business_key:str ):
        query = f"SELECT {business_key} from {table_name}"

        with self.db_client.get_olap_connection() as conn:
            df_dw = pd.read_sql(text(query), conn)
            valid_keys = df_dw[business_key].tolist()

            df_load = df_transformer[~df_transformer[business_key].isin(valid_keys)]

            df_load.to_sql(table_name, conn, if_exists='append', index=False)









