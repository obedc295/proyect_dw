from math import trunc

from src.infrastructure.db_client import DatabaseClient
from sqlalchemy import text, result_tuple
import pandas as pd

def test_conexiones():
    database_client = DatabaseClient()
    try:
        with database_client.get_oltp_connection() as connection:
            resultado = connection.execute(text('SELECT 1')).scalar()
            conexion_viva_1 = True if resultado == 1 else False
    except Exception:
            conexion_viva_1 = False

    assert conexion_viva_1 is True

    try:
        with database_client.get_olap_connection() as connection:
            resultado = connection.execute(text('SELECT 1')).scalar()
            conexion_viva_2 = True if resultado == 1 else False
    except Exception:
        conexion_viva_2 = False

    assert conexion_viva_2 is True












