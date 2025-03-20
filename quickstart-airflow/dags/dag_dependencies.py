# Este es un ejemplo de un DAG en Airflow con dependencias entre tareas.

# Importar las librerías necesarias
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Definir funciones para cada tarea
def tarea_inicio():
    """
    Esta función se ejecuta al inicio del DAG.
    Se puede utilizar para inicializar variables o realizar configuraciones iniciales.
    """
    print('Inicio del proceso')

def tarea_proceso():
    """
    Esta función representa el proceso principal del DAG.
    Aquí se pueden realizar las operaciones necesarias, como la carga de datos,
    transformaciones, etc.
    """
    print('Procesando datos...')

def tarea_fin():
    """
    Esta función se ejecuta al final del DAG.
    Se puede utilizar para limpiar recursos, enviar notificaciones, etc.
    Se asegura de que todas las tareas anteriores se hayan completado antes de
    ejecutar esta tarea.
    """
    print('Proceso finalizado')

# Definir el DAG
with DAG(
    'simple_dependency',            # Nombre del DAG
    start_date=datetime(2025, 1, 1),    # Fecha de inicio
    schedule_interval='@daily',         # Intervalo de programación
    catchup=False                       # No ejecutar tareas pasadas
) as dag:

    # Tarea de inicio
    # Se define la tarea de inicio utilizando el operador PythonOperator.
    inicio = PythonOperator(
        task_id='inicio',               # ID de la tarea
        python_callable=tarea_inicio    # Función a ejecutar
    )

    # Tarea de proceso
    # Se define la tarea de proceso utilizando el operador PythonOperator.
    # Esta tarea se ejecutará después de que la tarea de inicio haya finalizado.
    # La tarea de proceso depende de la tarea de inicio.
    proceso = PythonOperator(
        task_id='proceso',              # ID de la tarea
        python_callable=tarea_proceso   # Función a ejecutar
    )

    # Tarea de fin
    # Se define la tarea de fin utilizando el operador PythonOperator.
    # Esta tarea se ejecutará después de que la tarea de proceso haya finalizado.
    # La tarea de fin depende de la tarea de proceso.
    fin = PythonOperator(
        task_id='fin',                # ID de la tarea
        python_callable=tarea_fin     # Función a ejecutar
    )

    # Definir las dependencias entre las tareas 
    # La tarea de inicio debe completarse antes de que comience la tarea de proceso.
    # La tarea de proceso debe completarse antes de que comience la tarea de fin.
    inicio >> proceso >> fin
