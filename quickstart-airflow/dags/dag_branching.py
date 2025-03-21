# Este DAG de Airflow muestra cómo usar un operador BranchPythonOperator 
# para decidir qué tarea ejecutar a continuación en función de un valor aleatorio generado.

# # Importar las librerías necesarias de Airflow
from airflow import DAG
from airflow.operators.python import BranchPythonOperator
from airflow.operators.empty import EmptyOperator
import random
from datetime import datetime

# Función para decidir qué rama ejecutar
def elegir_rama():
    """
    Genera un valor aleatorio y decide la ruta a seguir.
    """
    # Generar un valor aleatorio entre 1 y 10
    valor = random.randint(1, 10)
    
    # Imprimir el valor generado
    print(f"Valor aleatorio generado: {valor}")

    # Decidir la ruta a seguir
    # Si el valor es mayor que 5, seguir la ruta 'tarea_mayor_5'
    if valor > 5:
        return 'tarea_mayor_5'
    else:
        return 'tarea_menor_5'


# Definir el DAG
with DAG(
    dag_id='simple_branching',          # Nombre del DAG
    start_date=datetime(2025, 1, 1),    # Fecha de inicio del DAG
    schedule_interval='@daily',         # Intervalo de programación
    catchup=False                       # No ejecutar tareas pasadas
) as dag:

    # Tarea de branching
    # Se define la tarea de branching utilizando el operador BranchPythonOperator.
    eleccion_ruta = BranchPythonOperator(
        task_id='eleccion_ruta',        # ID de la tarea
        python_callable=elegir_rama     # Función a ejecutar
    )

    # Tareas finales
    # Se definen las tareas finales utilizando el operador EmptyOperator.
    # Estas tareas no realizan ninguna acción, pero se utilizan para representar
    # las ramas del DAG.
    # Estas tareas se ejecutarán dependiendo de la ruta elegida.
    # Si la ruta elegida es 'tarea_mayor_5', se ejecutará esta tarea.
    # Si la ruta elegida es 'tarea_menor_5', se ejecutará esta tarea.
    tarea_mayor_5 = EmptyOperator(task_id='tarea_mayor_5')  
    tarea_menor_5 = EmptyOperator(task_id='tarea_menor_5')

    # Tarea de finalización
    # Se define la tarea de finalización utilizando el operador EmptyOperator.
    # Esta tarea se ejecutará después de que se complete cualquiera de las tareas
    # anteriores, independientemente de la ruta elegida.
    # La regla de activación es 'none_failed_or_skipped', lo que significa que
    # la tarea de finalización se ejecutará incluso si alguna de las tareas anteriores
    # falla o se omite.
    fin = EmptyOperator(task_id='fin', trigger_rule='none_failed_or_skipped')

    # Definir el flujo del DAG
    # La tarea de branching se ejecuta primero.
    # Luego, dependiendo del valor aleatorio generado, se ejecutará una de las
    # tareas finales (tarea_mayor_5 o tarea_menor_5).
    # Finalmente, se ejecuta la tarea de finalización.
    eleccion_ruta >> [tarea_mayor_5, tarea_menor_5] >> fin
