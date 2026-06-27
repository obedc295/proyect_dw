import pandas as pd
from src.services.transformer import DataTransformer


def test_transformaciones_pandas():
    datos_prueba = {
        'Nombre': ['Honduras', 'Cabo Verde'],
        'CodigoRegion': ['HN', 'CBV'],
        'Fecha': ['06-11-2026', '06-26-2026']
    }

    df_prueba= pd.DataFrame(datos_prueba)

    transformer = DataTransformer()

    transformer.capitalize_transform(df_prueba, 'Nombre', 'NOMBRE MAYUSCULA', 'upper')
    transformer.concat_transform(df_prueba, 'Nombre CodigoRegion', 'Nombre', 'CodigoRegion')
    transformer.date_transform(df_prueba, 'Fecha', 'Anio','year')

    assert df_prueba.iloc[0]['NOMBRE MAYUSCULA'] == 'HONDURAS'
    assert df_prueba.iloc[1]['Nombre CodigoRegion'] == 'Cabo Verde CBV'
    assert df_prueba.iloc[0]['Anio'] == 2026
