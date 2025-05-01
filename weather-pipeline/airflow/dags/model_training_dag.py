# DAG para el entrenamiento y evaluación de un modelo de predicción de lluvia

# Manejo de rutas y configuración
#   de ruta de modulo
import sys
import os
sys.path.append('/opt/airflow/scripts')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from datetime import datetime
import model_utils as model_utils
from db_utils import log_model_metrics

# Argumentos por defecto para las tareas
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

# Variables globales del DAG
models_dir = "/opt/airflow/models/"


# --- Definición de funciones para las tareas del DAG ---
def load_and_preprocess_task(**context):
    """
    Carga y preprocesa los datos, luego realiza el split de train/test.
    Deja X_train, X_test, y_train, y_test en XComs.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    # Se carga el DataFrame desde PostgreSQL y se preprocesa
    df = model_utils.load_data_from_postgres()
    # Se preprocesa el DataFrame y se separa en conjuntos de entrenamiento y prueba
    #   Se separa el DataFrame en características (X) y etiquetas (y)
    X_train, X_test, y_train, y_test = model_utils.preprocess_data(df=df)

    # Enviar a XCom los conjuntos de datos
    context['ti'].xcom_push(key="X_train", value=X_train)
    context['ti'].xcom_push(key="X_test", value=X_test)
    context['ti'].xcom_push(key="y_train", value=y_train)
    context['ti'].xcom_push(key="y_test", value=y_test)

def train_task(**context):
    """
    Entrena el modelo usando los datos de entrenamiento.
    Guarda el modelo en XCom.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    # Se obtienen los datos de entrenamiento desde XCom
    X_train = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="X_train")
    y_train = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="y_train")
    # Se entrena el modelo usando los datos de entrenamiento
    #   Se guarda el modelo en XCom para su posterior uso
    model = model_utils.train_model(X_train, y_train)
    context['ti'].xcom_push(key="model", value=model)

def evaluate_task(**context):
    """
    Evalúa el modelo usando los datos de prueba.
    Guarda las métricas en XCom.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    # Se obtienen el modelo y los datos de prueba desde XCom
    model = context['ti'].xcom_pull(task_ids="train_model", key="model")
    X_test = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="X_test")
    y_test = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="y_test")
    # Se evalúa el modelo usando los datos de prueba
    #   Se guardan las métricas en XCom para su posterior uso
    metrics = model_utils.evaluate_model(model, X_test, y_test)
    context['ti'].xcom_push(key="metrics", value=metrics)

def save_task(**context):
    """
    Guarda el modelo entrenado como archivo .pkl
    Guarda también las métricas en la base de datos.

    Args:
        context (dict): Contexto de Airflow que contiene información sobre la tarea y el DAG.

    Returns:
        None
    """
    # Se obtienen el modelo y las métricas desde XCom
    model = context['ti'].xcom_pull(task_ids="train_model", key="model")
    metrics = context['ti'].xcom_pull(task_ids="evaluate_model", key="metrics")
    #Se utiliza la función get_next_model_version para obtener la versión del modelo
    model_version = model_utils.get_next_model_version(models_dir)
    model_path = f"{models_dir}model_{model_version}.pkl"
    # Se guarda el modelo y las métricas en la base de datos
    #   Se utiliza la función save_model para guardar el modelo 
    #   y save_metrics_to_db para guardar las métricas
    model_utils.save_model(model, model_path)
    log_model_metrics(metrics=metrics, model_path=model_path, model_version=model_version)

# --- Definición del DAG ---
# Se define el DAG para el entrenamiento y evaluación de un modelo de predicción de lluvia
with DAG(
    dag_id="model_training_dag",                        # Nombre del DAG
    default_args=default_args,                          # Argumentos por defecto para las tareas
    description="DAG mensual para entrenamiento y " \
    "evaluación de modelo de predicción de lluvia",     # Descripción del DAG
    schedule_interval="@monthly",                       # Programación automática mensual
    start_date=datetime(2025, 5, 1),                    # Fecha de inicio del DAG
    catchup=False,                                      # No se ejecutan tareas pasadas
    tags=["training", "ml", "weather"],                 # Etiquetas para el DAG
) as dag:
    
    # Se definen las tareas del DAG
    # Tarea para cargar y preprocesar los datos
    load_and_preprocess = PythonOperator(
        task_id="load_and_preprocess_data",
        python_callable=load_and_preprocess_task,
        provide_context=True
    )

    # Tarea para entrenar el modelo
    train = PythonOperator(
        task_id="train_model",
        python_callable=train_task,
        provide_context=True
    )

    # Tarea para evaluar el modelo
    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_task,
        provide_context=True
    )

    # Tarea para guardar el modelo y las métricas
    save = PythonOperator(
        task_id="save_model_and_metrics",
        python_callable=save_task,
        provide_context=True
    )

    # Task para disparar el DAG de monitoreo
    trigger_monitoring_dag = TriggerDagRunOperator(
        task_id='trigger_model_monitoring_dag',
        trigger_dag_id='model_monitoring_dag',
        wait_for_completion=False,  # True si quieres que espere respuesta
        reset_dag_run=True,         # Reinicia si ya existe un run previo
        execution_date="{{ ds }}"   # Pasa la fecha de ejecución
    )


    # Definición de la secuencia de tareas
    # Primero se cargan y preprocesan los datos, luego se entrena el modelo,
    #   se evalúa y finalmente se guarda el modelo y las métricas
    #   Después se dispara el DAG de monitoreo
    load_and_preprocess >> train >> evaluate >> save >> trigger_monitoring_dag

