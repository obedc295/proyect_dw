import os
import urllib
from dotenv import load_dotenv

# Cargar las variables del archivo .env
load_dotenv()

class Settings:
    # Formato limpio y directo compatible con SQLAlchemy y pyodbc para autenticación de Windows
    raw_oltp = (
        f"DRIVER={os.getenv('OLTP_DRIVER')};"
        f"SERVER={os.getenv('OLTP_SERVER')};"
        f"DATABASE={os.getenv('OLTP_DATABASE')};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    
    raw_olap = (
        f"DRIVER={os.getenv('OLAP_DRIVER')};"
        f"SERVER={os.getenv('OLAP_SERVER')};"
        f"DATABASE={os.getenv('OLAP_DATABASE')};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )
    
    # El quote_plus asegura que la barra invertida '\' se transforme correctamente en caracteres URL (%5C)
    OLTP_URL = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(raw_oltp)}"
    OLAP_URL = f"mssql+pyodbc:///?odbc_connect={urllib.parse.quote_plus(raw_olap)}"

# Instancia global
settings = Settings()