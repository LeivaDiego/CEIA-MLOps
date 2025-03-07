from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Definir la función que se ejecutará en el DAG
def saludar():
    print('¡Hola, Airflow!')

# Definir el DAG
with DAG(
    'dag_hola_mundo',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    tarea_saludo = PythonOperator(
        task_id='saludo',
        python_callable=saludar
    )

    tarea_saludo
