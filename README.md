# Sistema ETL Dinámico para Data Warehouse

Este proyecto implementa un sistema ETL (Extracción, Transformación y Carga) dinámico y modular diseñado en capas. Permite extraer datos desde una base de datos transaccional (OLTP), aplicar transformaciones configurables en tiempo de ejecución (como conversión de texto, concatenaciones y extracción de componentes de fecha) mediante Pandas, y cargar los resultados de forma incremental en un Data Warehouse (OLAP) utilizando SQLAlchemy para evitar la duplicación de registros mediante llaves de negocio. El sistema cuenta con una interfaz gráfica interactiva desarrollada en Streamlit y pruebas unitarias automatizadas con Pytest.

---

## Requisitos Previos

Antes de comenzar, asegúrese de tener instalado lo siguiente en su sistema:
* Python 3.10 o superior.
* Microsoft SQL Server (con las bases de datos origen y destino creadas).
* ODBC Driver 17 for SQL Server.

---

## Guía de Instalación y Configuración

Siga estos pasos de manera secuencial para desplegar el proyecto en su entorno local:

### 1. Descargar el Proyecto desde GitHub
Clone el repositorio en su máquina local utilizando Git o descargue el código fuente:


``` bash
git clone https://github.com/obedc295/proyecto_dw.git
cd proyecto_dw
```



### 2. Configurar el Ambiente Virtual de Python
Cree un entorno virtual aislado para el proyecto y actívelo en su terminal:

En Windows (PowerShell/CMD):

```Bash
python -m venv .venv
.venv\Scripts\activate
```
En Linux/WSL/macOS:
```Bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3.Instalar las Librerías y Dependencias
Con el entorno virtual activado, instale todos los paquetes requeridos listados en el archivo de requerimientos:

```Bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configurar las Variables de Entorno
Cree un archivo llamado .env en la raíz del proyecto (al mismo nivel que app.py). Este archivo almacenará las credenciales y parámetros de conexión de sus bases de datos.

A continuación, se presenta un ejemplo de configuración utilizando la base de datos Northwind como origen:
``` .env
Configuración de la Base de Datos Origen (OLTP)

OLTP_SERVER=ELIEL\SQLEXPRESS
OLTP_DATABASE=NORTHWND
OLTP_DRIVER=ODBC Driver 17 for SQL Server

Configuración de la Base de Datos Destino (Data Warehouse / OLAP)
OLAP_SERVER=ELIEL\SQLEXPRESS
OLAP_DATABASE=DW_NORTHWIND
OLAP_DRIVER=ODBC Driver 17 for SQL Server

```


### Ejecución del Proyecto
Ejecutar la Interfaz Gráfica (Streamlit)
Una vez configurado el archivo .env, puede iniciar la aplicación web interactiva ejecutando el siguiente comando en su terminal:

```Bash
streamlit run app.py
```
El comando levantará un servidor local y abrirá automáticamente una pestaña en su navegador web (por lo general en http://localhost:8501) con el panel de control del sistema ETL.

Ejecutar las Pruebas Automatizadas
Para verificar que la infraestructura, los transformadores, el cargador incremental y el orquestador estén operando correctamente, ejecute la suite de pruebas con Pytest:

```Bash
pytest tests/ -v
```
