import pandas as pd
from src.services.extractor import DataExtractor
from src.services.transformer import DataTransformer
from src.services.loader import DataLoader


class ETLPipeline:
    def __init__(self, db_client):
        self.extractor = DataExtractor(db_client)
        self.transformer = DataTransformer()
        self.loader = DataLoader(db_client)

    def run_dynamic_etl(self, source_table: str, target_table: str, business_key: str, column_mappings: list[dict], sql_query: str | None = None):
        """
        Ejecuta un flujo ETL dinámico basado en una lista de mapeos columna-por-columna.

        column_mappings ejemplo: [
            {
                "source_column": "Name",
                "transform_type": "upper",
                "target_column": "CustomerName"
            },
            {
                "type": "concat",
                "column1": "FirstName",
                "column2": "LastName",
                "target_column": "FullName"
            }
        ]
        """
        # 1. EXTRAER
        if source_table:
            columns_to_extract = list(set(
                m["source_column"] for m in column_mappings if m.get("type") != "concat"
            ) | set(
                m["column1"] for m in column_mappings if m.get("type") == "concat"
            ) | set(
                m["column2"] for m in column_mappings if m.get("type") == "concat"
            ))
            df = self.extractor.extract_by_table(source_table, columns=columns_to_extract)
            total_extraidos = len(df)
        if sql_query:
            df = self.extractor.extract_by_query(sql_query)
            total_extraidos = len(df)

        # 2. TRANSFORMAR
        for mapping in column_mappings:
            if mapping.get("type") == "concat":
                self.transformer.concat_transform(df,
                    new_column=mapping["target_column"],
                    column1=mapping["column1"],
                    column2=mapping["column2"])
            else:
                ttype = mapping["transform_type"]
                source_col = mapping["source_column"]
                target_col = mapping["target_column"]

                if ttype == "none":
                    df[target_col] = df[source_col]
                elif ttype in ("upper", "lower"):
                    self.transformer.capitalize_transform(df,
                        column=source_col,
                        new_column=target_col,
                        operation=ttype)
                elif ttype in ("year", "month", "day"):
                    self.transformer.date_transform(df,
                        column=source_col,
                        new_column=target_col,
                        operation=ttype)

        # 3. SELECCIONAR solo las columnas mapeadas + business key
        target_cols = list(set(
            [m["target_column"] for m in column_mappings] + [business_key]
        ))
        df_load = df[target_cols]

        # 4. CARGAR
        rows_loaded = self.loader.load_incremental(df_load,
                                     table_name=target_table,
                                     business_key=business_key)
        return {
            "status": "success",
            "rows_extracted": total_extraidos,
            "rows_loaded": rows_loaded,
            "table_destination": target_table,
            "sample_data": df_load.head(5)
        }