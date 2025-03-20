# Este es un ejemplo de un DAG de Airflow que utiliza el BashOperator para ejecutar un comando Bash.

# Importar las librerías necesarias de Airflow
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Definir el DAG
with DAG(
    'simple_bash_operator',             # Nombre del DAG
    start_date=datetime(2025, 1, 1),    # Fecha de inicio del DAG
    schedule_interval='@daily',         # Intervalo de programación
    catchup=False                       # No ejecutar tareas pasadas
) as dag:

    # Definir una tarea con BashOperator
    # Crear un operador Bash que ejecutará un comando Bash 
    tarea_bash = BashOperator(
        task_id='comando_bash',     # ID de la tarea
        # Comando Bash a ejecutar
        # En este caso, simplemente imprime un mensaje en la consola
        bash_command="echo 'Este es un comando Bash ejecutado desde Airflow'" 
    )

    tarea_bash
