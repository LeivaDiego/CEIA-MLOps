# Este es un ejemplo de un DAG simple en Apache Airflow que imprime un saludo en la consola.

# Importar las librerías necesarias de Airflow
from airflow import DAG                             
from airflow.operators.python import PythonOperator
from datetime import datetime

# Definir la función que se ejecutará en el DAG
def saludar():
    """
    Función que imprime un saludo en la consola.
    """
    print('¡Hola, Airflow!')

# Definir el DAG
with DAG(
    'hello_world',                  # Nombre del DAG
    start_date=datetime(2025, 1, 1),    # Fecha de inicio del DAG
    schedule_interval='@daily',         # Intervalo de programación
    catchup=False                       # No ejecutar tareas pasadas
) as dag:       

    # Definir la tarea que ejecutará la función saludar
    # Crear un operador Python que ejecutará la función saludar
    tarea_saludo = PythonOperator(
        task_id='saludo',            # ID de la tarea
        python_callable=saludar     # Función a ejecutar
    )

    tarea_saludo    # Establecer la tarea como parte del DAG
