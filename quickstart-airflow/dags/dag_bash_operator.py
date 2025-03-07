from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Definir el DAG
with DAG(
    'dag_bash_example',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Definir una tarea con BashOperator
    tarea_bash = BashOperator(
        task_id='comando_bash',
        bash_command="echo 'Este es un comando Bash ejecutado desde Airflow'"
    )

    tarea_bash
