# DAG para inicializar la base de datos con datos de clima.

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import scripts.db_utils as db_utils  # Importa funciones de utilidades de base de datos

# Argumentos por defecto para las tareas
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

# --- Definición del DAG ---
# Se define el DAG para inicializar la base de datos con datos de clima
with DAG(
    dag_id='database_bootstrap_dag',                # Nombre del DAG
    default_args=default_args,                      # Argumentos por defecto para las tareas
    description='Bootstrap de la base de datos',    # Descripción del DAG
    schedule_interval=None,                         # No hay programación automática
                                                    #   Se ejecuta una vez al iniciar el DAG
    start_date=datetime(2025, 5, 1),                # Fecha de inicio del DAG
    catchup=False,                                  # No se ejecutan tareas pasadas
    tags=['bootstrap', 'database'],                 # Etiquetas para el DAG
) as dag:

    # Se definen las tareas del DAG
    # Tarea para crear la tabla de datos de clima
    create_weather_table_task = PythonOperator(
        task_id='create_weather_table',
        python_callable=db_utils.create_weather_table
    )

    # Tarea para crear la tabla de log de errores en validación
    create_log_table_task = PythonOperator(
        task_id='create_log_table',
        python_callable=db_utils.create_validation_log_table
    )

    # Tarea para crear la tabla de metricas de modelo
    create_metrics_table_task = PythonOperator(
        task_id='create_metrics_table',
        python_callable=db_utils.create_model_metrics_table
    )

    # Tarea para insertar datos de clima en la tabla
    insert_data_task = PythonOperator(
        task_id='insert_weather_data',
        python_callable=db_utils.insert_history_data

    )

    # Definición de la secuencia de tareas
    # Primero se crea la tabla y luego se insertan los datos
    create_weather_table_task >> create_log_table_task >> create_metrics_table_task >> insert_data_task