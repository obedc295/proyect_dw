from src.services.pipeline import ETLPipeline
from unittest.mock import MagicMock
import pandas as pd


def test_flujo_completo_con_datos_reales():
    # 1. PREPARAR
    mock_db_client = MagicMock()
    pipeline = ETLPipeline(mock_db_client)

    tabla_origen = "Sales.SalesTerritory"
    tabla_destino = "DimTerritory"
    llave_negocio = "TerritoryID"

    config_transformacion = {
        "type": "capitalize",
        "column": "Name",
        "new_column": "New_Name",
        "operation": "upper"
    }

    # Datos simulados para el extractor
    datos_origen = {
        "TerritoryID": [1, 2, 3],
        "Name": ["northwest", "southeast", "central"],
        "CountryRegionCode": ["US", "US", "US"]
    }
    df_origen = pd.DataFrame(datos_origen)

    # Mockeamos extractor y loader para evitar base de datos real
    pipeline.extractor.extract_by_table = MagicMock(return_value=df_origen)
    pipeline.loader.load_incremental = MagicMock()

    # 2. ACTUAR
    resultado = pipeline.run_dynamic_etl(
        source_table=tabla_origen,
        target_table=tabla_destino,
        business_key=llave_negocio,
        transform_config=config_transformacion
    )

    # 3. AFIRMAR
    assert resultado["status"] == "success"
    assert resultado["rows_extracted"] == 3

    # Verificar que el loader recibió el DataFrame transformado
    df_cargado = pipeline.loader.load_incremental.call_args[0][0]

    # Verificar que la columna 'New_Name' se haya creado correctamente en mayúsculas
    assert "New_Name" in df_cargado.columns
    assert df_cargado.iloc[0]["New_Name"] == "NORTHWEST"
    assert df_cargado.iloc[1]["New_Name"] == "SOUTHEAST"