# DAG para monitorear el rendimiento de modelos válidos

# Manejo de rutas y configuración
#   de ruta de modulo
import sys
import os
sys.path.append('/opt/airflow/scripts')

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import model_utils as model_utils

# --- Configuración del logger ---
# Se importa el logger desde el módulo de utilidades de logging
from log_utils import get_logger
logger = get_logger(__name__)

# Argumentos por defecto para las tareas
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

# --- Definición del DAG ---
# Se define el DAG para monitorear el rendimiento de modelos válidos
with DAG(
    dag_id='model_monitoring_dag',              # ID del DAG
    default_args=default_args,                  # Argumentos por defecto para las tareas
    description='Monitorea el rendimiento ' \
    'de modelos válidos',                       # Descripción del DAG
    schedule_interval=None,                     # No se programa automáticamente 
                                                #   (Se ejecuta con Trigger)
    start_date=datetime(2025, 5, 1),            # Fecha de inicio del DAG
    catchup=False,                              # No se ejecutan tareas pasadas
    tags=['model', 'monitoring'],               # Etiquetas para el DAG
) as dag:   

    # Se definen las tareas del DAG
    # Tarea para cargar los modelos válidos desde el almacenamiento
    compare_task = PythonOperator(
        task_id='compare_latest_models',
        python_callable=model_utils.compare_models,
        provide_context=True
    )