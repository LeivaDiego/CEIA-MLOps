from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Definir funciones para cada tarea
def tarea_inicio():
    print('Inicio del proceso')

def tarea_proceso():
    print('Procesando datos...')

def tarea_fin():
    print('Proceso finalizado')

# Definir el DAG
with DAG(
    'dag_con_dependencias',
    start_date=datetime(2023, 1, 1),
    schedule_interval='@daily',
    catchup=False
) as dag:

    # Tarea de inicio
    inicio = PythonOperator(
        task_id='inicio',
        python_callable=tarea_inicio
    )

    # Tarea de proceso
    proceso = PythonOperator(
        task_id='proceso',
        python_callable=tarea_proceso
    )

    # Tarea de fin
    fin = PythonOperator(
        task_id='fin',
        python_callable=tarea_fin
    )

    # Definir las dependencias
    inicio >> proceso >> fin
