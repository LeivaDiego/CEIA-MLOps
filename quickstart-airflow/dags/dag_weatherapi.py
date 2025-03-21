# Este DAG consulta la API de WeatherAPI para obtener datos del clima en Guatemala,
# exporta los resultados a un archivo JSON y utiliza un FileSensor para monitorear
# la creación del archivo exportado. Además, utiliza XCom para pasar datos entre tareas.

# Importar librerías necesarias
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from airflow.models import Variable
from datetime import timedelta
import requests
import json
import logging
import os

# Configuraciones generales
CITY = "Guatemala"      
JSON_FILE_PATH = "/opt/airflow/data/weather_result.json"

default_args = {
    'owner': 'airflow',
    'retries': 2,
    'retry_delay': timedelta(minutes=1),
}

# Tarea 1: Obtener datos del clima desde WeatherAPI
def fetch_weather_data(**kwargs):
    """
    Consulta la API de WeatherAPI y obtiene datos del clima.
    
    Args:
        **kwargs: Argumentos de contexto de Airflow.

    Raises:
        ValueError: Si no se encuentra la variable de API Key en Airflow.
        requests.RequestException: Si hay un error en la petición HTTP.

    Returns:
        None: Los datos del clima se almacenan en XCom.
    """
    # Obtener la API Key de las variables de Airflow
    # Asegúrate de que la variable 'weatherapi_key' esté configurada en Airflow
    api_key = Variable.get("weatherapi_key", default_var=None)
    if not api_key:
        raise ValueError("No se encontró la variable 'weatherapi_key' en Airflow.")

    # Configurar el endpoint de la API 
    # Visitar: https://www.weatherapi.com/docs/ 
    # para más detalles sobre la API y sus parámetros

    # Endpoint para obtener el clima actual sin datos de calidad del aire
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q={CITY}&aqi=no"   
    
    # Realizar la petición a la API
    try:
        response = requests.get(url, timeout=10)        # Timeout de 10 segundos
        response.raise_for_status()                     # Lanza un error si la respuesta no es 200
        data = response.json()                          # Convertir la respuesta a JSON
    
    except requests.RequestException as e:
        # Manejo de errores de la petición
        logging.error(f"Error al hacer la petición a WeatherAPI: {e}")
        raise requests.RequestException(f"Error al hacer la petición a WeatherAPI: {e}")

    # Obtener los datos relevantes de la respuesta
    current = data.get("current", {})   # Obtener los datos actuales
    location = data.get("location", {})  # Obtener la ubicación

    # Verificar si la respuesta contiene datos
    # Si no se encuentra la sección "current", lanzar un error    
    if not current:
        logging.error("No se encontraron datos actuales en la respuesta de WeatherAPI.")
        raise ValueError("No se encontraron datos actuales en la respuesta de WeatherAPI.")

    result = {
        "datetime": location.get("localtime"),
        "city": location.get("name"),
        "condition": current.get("condition", {}).get("text"),
        "temperature_c": current.get("temp_c"),
        "wind_kph": current.get("wind_kph"),
        "humidity": current.get("humidity")
    }

    # Guardar los datos en XCom para ser utilizados por la siguiente tarea
    logging.info(f"Datos del clima obtenidos: {result}")
    kwargs['ti'].xcom_push(key='weather_result', value=result)  


# Tarea 2: Exportar los datos obtenidos a un archivo JSON
def export_weather_data(**kwargs):
    """
    Exporta los datos del clima obtenidos a un archivo JSON.
    
    Args:
        **kwargs: Argumentos de contexto de Airflow.

    Raises:
        ValueError: Si no se encuentra el resultado del clima en XCom.
        IOError: Si hay un error al escribir el archivo JSON.

    Returns:
        None: Los datos se escriben en un archivo JSON.
    """
    # Obtener el resultado del clima desde XCom
    result = kwargs['ti'].xcom_pull(key='weather_result', task_ids='fetch_weather_data')
    
    # Verificar si se obtuvo el resultado
    if not result:
        raise ValueError("No se encontró el resultado del clima en XCom.")

    # Crear el directorio si no existe
    os.makedirs(os.path.dirname(JSON_FILE_PATH), exist_ok=True)
    
    # Escribir los datos en un archivo JSON
    try:
        # Guardar los datos en un archivo JSON
        with open(JSON_FILE_PATH, 'w') as f:
            json.dump(result, f)
        logging.info(f"Datos exportados correctamente en {JSON_FILE_PATH}")
    
    # Manejo de errores al escribir el archivo
    except Exception as e:
        logging.error(f"Error al escribir el archivo JSON: {e}")
        raise IOError(f"Error al escribir el archivo JSON: {e}")

# Definición del DAG
with DAG(
    dag_id="weather_consult",                                                            # Nombre del DAG
    description="Consulta de clima con WeatherAPI + XCom + monitoreo con FileSensor",   # Descripción del DAG
    default_args=default_args,                                                          # Argumentos por defecto
    schedule_interval="@daily",                                                         # Intervalo de ejecución
    start_date=days_ago(1),                                                             # Fecha de inicio
    catchup=False,                                                                      # No ejecutar tareas pasadas
    tags=["weather", "api", "xcom"],                                                    # Etiquetas para el DAG
) as dag:

    # Definición de las tareas
    # Tarea 1: Obtener datos del clima
    fetch = PythonOperator(
        task_id="fetch_weather_data",
        python_callable=fetch_weather_data,
        provide_context=True,
    )

    # Tarea 2: Exportar datos a un archivo JSON
    # Se utiliza el mismo JSON_FILE_PATH definido anteriormente
    export = PythonOperator(
        task_id="export_weather_data",
        python_callable=export_weather_data,
        provide_context=True,
    )

    # Definir orden de ejecución
    fetch >> export
