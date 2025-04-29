from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import scripts.model_utils as model_utils

# --- Configuración del DAG ---
default_args = {
    'owner': 'airflow',
    'retries': 1,
}

# Variables globales del DAG
models_dir = "/opt/airflow/models/"

# Funciones para cada task

def load_and_preprocess_task(**context):
    """
    Carga y preprocesa los datos, luego realiza el split de train/test.
    Deja X_train, X_test, y_train, y_test en XComs.
    """
    df = model_utils.load_data_from_postgres()
    X_train, X_test, y_train, y_test = model_utils.preprocess_Data(X_train, y_train)

    # Enviar a XCom
    context['ti'].xcom_push(key="X_train", value=X_train)
    context['ti'].xcom_push(key="X_test", value=X_test)
    context['ti'].xcom_push(key="y_train", value=y_train)
    context['ti'].xcom_push(key="y_test", value=y_test)

def train_task(**context):
    """
    Entrena el modelo usando los datos de entrenamiento.
    Guarda el modelo en XCom.
    """
    X_train = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="X_train")
    y_train = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="y_train")
    
    model = model_utils.train_model(X_train, y_train)
    context['ti'].xcom_push(key="model", value=model)

def evaluate_task(**context):
    """
    Evalúa el modelo usando los datos de prueba.
    Guarda las métricas en XCom.
    """
    model = context['ti'].xcom_pull(task_ids="train_model", key="model")
    X_test = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="X_test")
    y_test = context['ti'].xcom_pull(task_ids="load_and_preprocess_data", key="y_test")
    
    metrics = model_utils.evaluate_model(model, X_test, y_test)
    context['ti'].xcom_push(key="metrics", value=metrics)

def save_task(**context):
    """
    Guarda el modelo entrenado como archivo .pkl
    Guarda también las métricas en la base de datos.
    """
    model = context['ti'].xcom_pull(task_ids="train_model", key="model")
    metrics = context['ti'].xcom_pull(task_ids="evaluate_model", key="metrics")

    model_version = model_utils.get_next_model_version(models_dir)
    model_path = f"{models_dir}model_{model_version}.pkl"

    model_utils.save_model(model, model_path)
    model_utils.save_metrics_to_db(metrics, model_version, datetime.today().date())

# --- Definición del DAG ---

with DAG(
    dag_id="model_training_dag",
    default_args=default_args,
    description="DAG mensual para entrenamiento y evaluación de modelo de predicción de lluvia",
    schedule_interval="@monthly",
    start_date=datetime(2025, 5, 1),
    catchup=False,
    tags=["training", "ml", "weather"],
) as dag:

    load_and_preprocess = PythonOperator(
        task_id="load_and_preprocess_data",
        python_callable=load_and_preprocess_task,
        provide_context=True
    )

    train = PythonOperator(
        task_id="train_model",
        python_callable=train_task,
        provide_context=True
    )

    evaluate = PythonOperator(
        task_id="evaluate_model",
        python_callable=evaluate_task,
        provide_context=True
    )

    save = PythonOperator(
        task_id="save_model_and_metrics",
        python_callable=save_task,
        provide_context=True
    )

    # Flujo del DAG
    load_and_preprocess >> train >> evaluate >> save
