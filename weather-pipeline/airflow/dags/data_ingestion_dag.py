# DAG para la ingesta diaria de datos de clima desde WeatherAPI

# Manejo de rutas y configuración
#   de ruta de modulo
import sys
import os
sys.path.append('/opt/airflow/scripts')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from api_utils import fetch_weather_data, update_local_csv
from db_utils import insert_weather_forecast, validate_row, log_validation_error
import pandas as pd


# --- Configuración del logger ---
# Se importa el logger desde el módulo de utilidades de logging
from log_utils import get_logger
logger = get_logger(__name__)


# Argumentos por defecto para las tareas
default_args = {
    'owner': 'airflow',
    'retries': 1,
}


# --- Definición de funciones para las tareas del DAG ---
def fetch_task(**context):
    """
    Tarea para obtener datos de clima desde WeatherAPI.
    Se obtiene la información del clima y se almacena en XCom para su posterior uso.
    
    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.
    
    Returns:
        None
    """
    # Llamada a la función para obtener datos del clima
    #   Se obtiene la información del clima y se almacena en XCom
    #   para su posterior uso en otras tareas
    weather_info = fetch_weather_data()

    if weather_info:
        context['ti'].xcom_push(key='weather_data', value=weather_info)
        logger.info("Datos del clima almacenados en XCom.")
    else:
        logger.warning("XCom no se actualizará.")


def validate_and_clean_task(**context):
    """
    Tarea para validar y limpiar los datos obtenidos del clima.
    Se valida la información y, si es correcta, se almacena en XCom para su posterior uso.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.
    
    Returns:
        None
    """
    try:
        # Se obtiene la información del clima desde XCom
        record = context['ti'].xcom_pull(task_ids='fetch_weather_data', key='weather_data')

        # Se crea un DataFrame a partir de la información obtenida 
        df = pd.DataFrame([record])
        row = df.iloc[0]

        # Se valida la información del clima
        reason = validate_row(row)
        if reason is None:
            # Si la información es válida, se almacena en XCom para su posterior uso
            context['ti'].xcom_push(key='validated_weather_data', value=record)
            logger.info("Datos del clima validados y almacenados en XCom.")
        else:
            # Si la información no es válida, se registra el error
            #   Se registra el error de validación en la base de datos
            log_validation_error(record, reason)
            
    except Exception as e:
        logger.error(f"Error inesperado durante la validación de datos: {e}")
        raise


def insert_into_postgres(**context):
    """
    Tarea para insertar los datos validados en la base de datos PostgreSQL.
    Se obtiene la información validada desde XCom y se inserta en la base de datos.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    try:
        # Se obtiene la información validada desde XCom
        data = context['ti'].xcom_pull(task_ids='validate_and_clean_data', key='validated_weather_data')

        # Se inserta la información en la base de datos PostgreSQL
        #   Se utiliza la función insert_weather_forecast para insertar los datos
        insert_weather_forecast(data)
        
    except Exception as e:
        logger.error(f"Error inesperado durante la inserción en PostgreSQL: {e}")
        raise


def update_csv_task(**context):
    """
    Tarea para actualizar el archivo CSV local con los datos validados.
    Se obtiene la información validada desde XCom y se actualiza el archivo CSV.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    try:
        # Se obtiene la información validada desde XCom
        data = context['ti'].xcom_pull(task_ids='validate_and_clean_data', key='validated_weather_data')
    
        # Se actualiza el archivo CSV local con la información validada
        #   Se utiliza la función update_local_csv para actualizar el archivo CSV
        update_local_csv(data)
    
    except Exception as e:
        logger.error(f"Error inesperado durante la actualización del archivo CSV: {e}")
        raise


# --- Definición del DAG ---
# Se define el DAG para la ingesta diaria de datos de clima desde WeatherAPI
with DAG(
    dag_id='data_ingestion_dag',                    # Nombre del DAG
    default_args=default_args,                      # Argumentos por defecto para las tareas
    description='Ingestión diaria de datos ' \
    'del clima desde WeatherAPI',                   # Descripción del DAG
    schedule_interval='@daily',                     # Programación automática diaria
    start_date=datetime(2025, 5, 1),                # Fecha de inicio del DAG
    catchup=False,                                  # No se ejecutan tareas pasadas
    tags=['ingestion', 'weatherapi'],               # Etiquetas para el DAG
) as dag:

    # Se definen las tareas del DAG
    # Tarea para obtener datos de clima desde WeatherAPI
    fetch_weather = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_task,
        provide_context=True
    )

    # Tarea para validar y limpiar los datos obtenidos del clima
    validate_and_clean = PythonOperator(
        task_id='validate_and_clean_data',
        python_callable=validate_and_clean_task,
        provide_context=True
    )

    # Tarea para insertar los datos validados en la base de datos PostgreSQL
    insert_into_db = PythonOperator(
        task_id='insert_into_postgres',
        python_callable=insert_into_postgres,
        provide_context=True
    )

    # Tarea para actualizar el archivo CSV local con los datos validados
    update_csv = PythonOperator(
        task_id='update_local_csv',
        python_callable=update_csv_task,
        provide_context=True
    )

    # Definición de la secuencia de tareas
    # Primero se obtienen los datos del clima, luego se validan y limpian,
    #   se insertan en la base de datos y finalmente se actualiza el archivo CSV local
    fetch_weather >> validate_and_clean >> insert_into_db >> update_csv 
