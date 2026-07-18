import streamlit as st
from src.infrastructure.db_client import DatabaseClient
from src.services.pipeline import ETLPipeline

st.set_page_config(page_title="ETL Dinámico", page_icon="📊", layout="wide")


@st.cache_resource
def init_etl():
    db_client = DatabaseClient()
    return db_client, ETLPipeline(db_client)


def _validar_y_ejecutar(pipeline, source_table, sql_query, target_table, business_key, column_mappings):
    errores = []
    if not source_table and not sql_query:
        errores.append("Debes seleccionar una tabla o escribir una consulta SQL.")
    if not target_table:
        errores.append("Debes especificar la tabla destino.")
    if not business_key:
        errores.append("Debes seleccionar la llave de negocio.")
    if not column_mappings:
        errores.append("Debes configurar al menos un mapeo de columna.")

    mapped_targets = [m["target_column"] for m in column_mappings]
    if business_key and business_key not in mapped_targets:
        errores.append(
            f"La llave de negocio '{business_key}' debe estar mapeada desde una columna origen."
        )

    for m in column_mappings:
        if m.get("type") == "concat":
            if not m.get("column1") or not m.get("column2"):
                errores.append("Cada concatenación debe tener dos columnas origen.")
        elif not m.get("source_column"):
            errores.append("Cada mapeo debe tener una columna origen.")
        if not m.get("target_column"):
            errores.append("Cada mapeo debe tener una columna destino.")

    if errores:
        for e in errores:
            st.error(e)
        return

    with st.spinner("Ejecutando ETL..."):
        try:
            resultado = pipeline.run_dynamic_etl(
                source_table=source_table or "",
                target_table=target_table,
                business_key=business_key,
                column_mappings=column_mappings,
                sql_query=sql_query,
            )

            st.success("ETL completado exitosamente")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Filas extraídas", resultado["rows_extracted"])
            with c2:
                st.metric("Filas cargadas", resultado["rows_loaded"])
            st.markdown(f"**Tabla destino:** `{resultado['table_destination']}`")

            with st.expander("Ver detalle completo de la respuesta"):
                st.json(resultado)

            st.subheader("Vista previa de datos cargados")
            st.dataframe(resultado["sample_data"], use_container_width=True)
        except Exception as e:
            st.error(f"Error durante la ejecución del ETL: {e}")


def main():
    st.title("Sistema ETL")
    st.markdown("---")

    try:
        db_client, pipeline = init_etl()
    except Exception as e:
        st.error(f"Error al inicializar la conexión a la base de datos: {e}")
        st.stop()

    col_source, col_target = st.columns(2)

    with col_source:
        st.subheader("Origen de datos")
        source_mode = st.radio(
            "Método de extracción",
            ["Tabla existente (OLTP)", "SQL personalizado"],
            horizontal=True,
        )

        source_table = None
        source_columns = []
        source_cols_info = []
        sql_query = None

        if source_mode == "Tabla existente (OLTP)":
            try:
                tables = pipeline.extractor.extract_tables()
                if tables:
                    source_table = st.selectbox("Selecciona una tabla", tables, key="source_table")
                    if source_table:
                        source_cols_info = db_client.get_source_columns(source_table)
                        col_names = [c["name"] for c in source_cols_info]
                        col_labels = [f"{c['name']}  ({c['type']})" for c in source_cols_info]
                        name_to_label = dict(zip(col_names, col_labels))
                        source_columns = st.multiselect(
                            "Columnas a extraer",
                            col_names,
                            default=col_names,
                            format_func=lambda x: name_to_label.get(x, x),
                            key="source_columns",
                            help="Selecciona las columnas que deseas transformar y mapear.",
                        )

                        preview_table = st.button("Vista previa", key="preview_table_btn", use_container_width=True)
                        if preview_table:
                            with st.spinner("Cargando vista previa..."):
                                try:
                                    preview_cols = source_columns or None
                                    df_preview = pipeline.extractor.extract_by_table(
                                        source_table, columns=preview_cols, limit=10
                                    )
                                    st.session_state.preview_df = df_preview
                                except Exception as e:
                                    st.error(f"Error al obtener vista previa: {e}")

                        if st.session_state.get("preview_df") is not None:
                            st.dataframe(st.session_state.preview_df, use_container_width=True)

                        with st.expander("Ver tipos de datos de origen", expanded=False):
                            for c in source_cols_info:
                                st.markdown(f"- **{c['name']}** `{c['type']}`")
                else:
                    st.warning("No se encontraron tablas en la base de datos OLTP.")
            except Exception as e:
                st.error(f"No se pudieron cargar las tablas: {e}")
        else:
            sql_query = st.text_area(
                "Escribe tu consulta SQL",
                placeholder="SELECT * FROM .. WHERE ..",
                height=120,
                key="sql_textarea",
            )

            if st.session_state.get("sql_cache_query") != sql_query:
                st.session_state.sql_cache_df = None
                st.session_state.sql_cache_columns = []

            ejecutar_sql = st.button("Ejecutar consulta", key="exec_sql_btn", use_container_width=True)
            if ejecutar_sql and sql_query.strip():
                with st.spinner("Ejecutando consulta..."):
                    try:
                        df_sql = pipeline.extractor.extract_by_query(sql_query, limit=50)
                        st.session_state.sql_cache_df = df_sql
                        st.session_state.sql_cache_columns = df_sql.columns.tolist()
                        st.session_state.sql_cache_query = sql_query
                    except Exception as e:
                        st.error(f"Error al ejecutar la consulta: {e}")

            if st.session_state.get("sql_cache_df") is not None:
                df_sql = st.session_state.sql_cache_df
                source_columns = st.session_state.sql_cache_columns
                source_cols_info = [{"name": c, "type": str(df_sql[c].dtype)} for c in source_columns]
                st.dataframe(df_sql, use_container_width=True)

    with col_target:
        st.subheader("Destino en el DW")
        target_table = None
        target_cols_info = []
        try:
            tablas_dw = db_client.get_olap_tables()
            if tablas_dw:
                target_table = st.selectbox(
                    "Selecciona la tabla destino",
                    tablas_dw,
                    key="target_table",
                )
                if target_table:
                    target_cols_info = db_client.get_target_columns(target_table)
                    with st.expander(f"Columnas en `{target_table}`", expanded=True):
                        for c in target_cols_info:
                            st.markdown(f"- **{c['name']}** `{c['type']}`")
            else:
                st.warning("No se encontraron tablas en el Data Warehouse.")
        except Exception as e:
            st.error(f"No se pudieron cargar las tablas del DW: {e}")

        target_col_names = [c["name"] for c in target_cols_info]
        target_col_labels = [f"{c['name']}  ({c['type']})" for c in target_cols_info]
        name_to_target_label = dict(zip(target_col_names, target_col_labels))

    st.markdown("---")
    st.subheader("Mapeo de columnas y transformaciones")

    if source_columns and target_col_names:
        col_headers = st.columns([2, 2, 3])
        with col_headers[0]:
            st.markdown("**Columna origen**")
        with col_headers[1]:
            st.markdown("**Transformación**")
        with col_headers[2]:
            st.markdown("**Columna destino**")

        st.divider()

        column_mappings = []
        for i, col in enumerate(source_columns):
            col_info = next((c for c in source_cols_info if c["name"] == col), None)
            col_type = col_info["type"] if col_info else ""

            row = st.columns([2, 2, 3])
            with row[0]:
                st.markdown(f"**{col}**  \n`{col_type}`")
            with row[1]:
                transform = st.selectbox(
                    "Transformación",
                    ["Ninguna", "Upper", "Lower", "Año", "Mes", "Día"],
                    key=f"tr_{i}_{col}",
                    label_visibility="collapsed",
                )
            with row[2]:
                target_opciones = ["— No mapear —"] + target_col_names
                target = st.selectbox(
                    "Columna destino",
                    target_opciones,
                    format_func=lambda x: name_to_target_label.get(x, x) if x in name_to_target_label else x,
                    key=f"tg_{i}_{col}",
                    label_visibility="collapsed",
                )

            transform_type = transform.lower() if transform != "Ninguna" else "none"
            if transform == "Upper":
                transform_type = "upper"
            elif transform == "Lower":
                transform_type = "lower"
            elif transform == "Año":
                transform_type = "year"
            elif transform == "Mes":
                transform_type = "month"
            elif transform == "Día":
                transform_type = "day"

            if target != "— No mapear —":
                column_mappings.append({
                    "source_column": col,
                    "transform_type": transform_type,
                    "target_column": target,
                })

        st.markdown("---")
        st.markdown("**Concatenaciones** (combinar 2 columnas en 1)")

        if "num_concat" not in st.session_state:
            st.session_state.num_concat = 0

        concat_mappings = []
        for i in range(st.session_state.num_concat):
            rc = st.columns([2, 2, 3])
            with rc[0]:
                col1 = st.selectbox(
                    "Columna 1",
                    source_columns,
                    key=f"concat_col1_{i}",
                    label_visibility="collapsed",
                )
            with rc[1]:
                col2 = st.selectbox(
                    "Columna 2",
                    source_columns,
                    key=f"concat_col2_{i}",
                    label_visibility="collapsed",
                )
            with rc[2]:
                target_concat = st.selectbox(
                    "Destino",
                    target_col_names,
                    format_func=lambda x: name_to_target_label.get(x, x),
                    key=f"concat_target_{i}",
                    label_visibility="collapsed",
                )
            concat_mappings.append({
                "type": "concat",
                "column1": col1,
                "column2": col2,
                "target_column": target_concat,
            })

        if st.button("+ Agregar concatenación", use_container_width=True):
            st.session_state.num_concat += 1
            st.rerun()

        if st.session_state.num_concat > 0:
            if st.button("- Quitar última concatenación", use_container_width=True):
                st.session_state.num_concat -= 1
                st.rerun()

        all_mappings = column_mappings + concat_mappings

        st.markdown("---")
        st.subheader("Configuración de carga")
        business_key = st.selectbox(
            "Llave de negocio (columna destino para carga incremental)",
            target_col_names,
            format_func=lambda x: name_to_target_label.get(x, x),
            key="business_key",
        )

        st.markdown("---")
        st.button(
            "Ejecutar ETL",
            type="primary",
            use_container_width=True,
            on_click=_validar_y_ejecutar,
            args=(
                pipeline,
                source_table,
                sql_query,
                target_table,
                business_key,
                all_mappings,
            ),
        )
    else:
        if source_table and target_table:
            if not source_columns:
                st.info("Selecciona columnas de origen o ejecuta una consulta SQL para configurar el mapeo.")
            if not target_col_names:
                st.info("La tabla destino no tiene columnas disponibles.")
        else:
            st.info("Selecciona una tabla de origen y una tabla destino para configurar el mapeo.")


if __name__ == "__main__":
    main()
