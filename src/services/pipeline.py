from src.services.extractor import DataExtractor
from src.services.transformer import DataTransformer
from src.services.loader import DataLoader


class ETLPipeline:
    def __init__(self, db_client):
        self.extractor = DataExtractor(db_client)
        self.transformer = DataTransformer()
        self.loader = DataLoader(db_client)

    def run_dynamic_etl(self, source_table: str, target_table: str, business_key: str, transform_config: dict , sql_query: str | None = None):
        """
        Ejecuta un flujo ETL dinámico basado en la configuración enviada desde la UI.

        transform_config ejemplo: {
            "type": "capitalize",
            "column": "Name",
            "operation": "upper"
        }
        """
        # 1. EXTRAER
        if source_table:
            df = self.extractor.extract_by_table(source_table)
            total_extraidos = len(df)
        if sql_query:
            df = self.extractor.extract_by_query(sql_query)
            total_extraidos = len(df)

        # 2. TRANSFORMAR
        if transform_config["type"] == "capitalize":
            df = self.transformer.capitalize_transform(
                df,
                column=transform_config["column"],
                new_column=transform_config["new_column"],
                operation=transform_config["operation"]
            )
        elif transform_config["type"] == "date":
            df = self.transformer.date_transform(
                df,
                column=transform_config["column"],
                new_column=transform_config["new_column"],
                operation=transform_config["operation"]
            )
        elif transform_config["type"] == "concat":
            df = self.transformer.concat_transform(df,
                                                   new_column=transform_config["new_column"],
                                                   column1=transform_config["column1"],
                                                   column2=transform_config["column2"])


        # 3. CARGAR
        self.loader.load_incremental(df,
                                     table_name=target_table,
                                     business_key=business_key)
        return {
            "status": "success",
            "rows_extracted": total_extraidos,
            "table_destination": target_table,
            "sample_data": df.head(5)
        }