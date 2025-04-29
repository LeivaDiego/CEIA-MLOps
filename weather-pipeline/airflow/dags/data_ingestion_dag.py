from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from scripts.api_utils import fetch_weather_data, update_local_csv
from scripts.db_utils import insert_weather_forecast, validate_row, log_validation_error
import pandas as pd

default_args = {
    'owner': 'airflow',
    'retries': 1,
}

def fetch_task(**context):
    weather_info = fetch_weather_data()
    context['ti'].xcom_push(key='weather_data', value=weather_info)

def validate_and_clean_task(**context):
    record = context['ti'].xcom_pull(task_ids='fetch_weather_data', key='weather_data')
    df = pd.DataFrame([record])
    row = df.iloc[0]
    is_valid, reason = validate_row(row)
    if is_valid:
        context['ti'].xcom_push(key='validated_weather_data', value=record)
    else:
        log_validation_error(record, reason)
        raise ValueError("ERROR | Validación fallida: datos incorrectos, no se procede a insertar.")

def insert_into_postgres(**context):
    data = context['ti'].xcom_pull(task_ids='validate_and_clean_data', key='validated_weather_data')
    insert_weather_forecast(data)

def update_csv_task(**context):
    data = context['ti'].xcom_pull(task_ids='validate_and_clean_data', key='validated_weather_data')
    update_local_csv(data)

# --- Definición del DAG ---
with DAG(
    dag_id='data_ingestion_dag',
    default_args=default_args,
    description='Daily ingestion of weather data from WeatherAPI (history of yesterday)',
    schedule_interval='@daily',
    start_date=datetime(2024, 5, 1),
    catchup=False,
    tags=['ingestion', 'weatherapi'],
) as dag:

    fetch_weather = PythonOperator(
        task_id='fetch_weather_data',
        python_callable=fetch_task,
        provide_context=True
    )

    validate_and_clean = PythonOperator(
        task_id='validate_and_clean_data',
        python_callable=validate_and_clean_task,
        provide_context=True
    )

    insert_into_db = PythonOperator(
        task_id='insert_into_postgres',
        python_callable=insert_into_postgres,
        provide_context=True
    )

    update_csv = PythonOperator(
        task_id='update_local_csv',
        python_callable=update_csv_task,
        provide_context=True
    )

    fetch_weather >> validate_and_clean >> insert_into_db >> update_csv
