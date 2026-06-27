from src.infrastructure.db_client import DatabaseClient
from src.services.extractor import DataExtractor
from src.services.transformer import DataTransformer


def iniciar_proyecto():
    print("=== 1. Verificación de Infraestructura ===")
    db_client = DatabaseClient()
    if not db_client.test_connections():
        return
    
    print("\n=== 2. Probando Capa de Extracción Dinámica ===")
    extractor = DataExtractor(db_client)
    transformer = DataTransformer()
    
    # --- PRUEBA A: Extracción por Tabla Directa (Requisito 5) ---
    print("\n[Prueba A] Extrayendo datos directos de la tabla 'Sales.SalesTerritory'...")
    try:
        df_territorios = extractor.extract_by_table("Sales.SalesTerritory")
        print(f"-> ¡Éxito! Se extrajeron {len(df_territorios)} filas.")
        num_columnas_anterior = (len(df_territorios.columns))

        print(df_territorios.iloc[:, 0:6])
        transformer.capitalize_transform(df_territorios, "Name", "name (lower)", "lower")
        transformer.concat_transform(df_territorios, "NAME ID", "Name", "CountryRegionCode")
        transformer.capitalize_transform(df_territorios, "NAME ID", "NAME ID", "upper")

        print("-------NUEVA TABLA-----------")
        print(df_territorios.iloc[:, num_columnas_anterior:])

    except Exception as e:
        print(f"[FALLO] Error en Prueba A: {e}")



if __name__ == "__main__":
    iniciar_proyecto()

