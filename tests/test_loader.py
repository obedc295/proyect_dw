from unittest.mock import MagicMock, patch
import pandas as pd
from src.services.loader import DataLoader

def test_carga_incremental_filtra_correctamente():
    mock_db_client = MagicMock()
    mock_connection = MagicMock()

    mock_db_client.get_olap_connection.return_value.__enter__.return_value = mock_connection

    df_dw_simulado = pd.DataFrame({"CustomerID": [10]})
    pd.read_sql = MagicMock(return_value=df_dw_simulado)

    loader = DataLoader(mock_db_client)

    datos_transformados = {
        "CustomerID": [10, 20],
        "Nombre": ["Juan", "Pedro"]
    }

    df_transformado = pd.DataFrame(datos_transformados)

    with patch.object(pd.DataFrame, "to_sql") as mock_to_sql:

        loader.load_incremental(
            df_transformado,
            table_name="DimCustomer",
            business_key="CustomerID"
        )

        mock_to_sql.assert_called_once()