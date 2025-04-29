# Modulo para obtener datos del clima de la API de WeatherAPI y actualizar el archivo CSV localmente.

# --- Librerías ---
# Solicitud HTTP
import requests
# Manejo de datos
import pandas as pd
# Variables de Airflow
from airflow.models import Variable
# Manejo de fechas y archivos
from datetime import datetime, timedelta
import csv
import os

# --- Configuración de la API ---
# Se obtiene la clave de API de las variables de Airflow
API_KEY = Variable.get("WEATHER_API_KEY")
# Se define la URL base de la API y la ciudad para la que se desea obtener el clima
BASE_URL = "http://api.weatherapi.com/v1/history.json"
# Se utiliza la ciudad de Guatemala como ejemplo
CITY = "Guatemala"


# --- Funciones ---

def fetch_weather_data():
    """
    Función para obtener datos del clima de la API de WeatherAPI.
    Esta función realiza una solicitud a la API para obtener el clima de ayer en la ciudad especificada.
    
    Args:
        None

    Returns:
        dict: Un diccionario con la información del clima, incluyendo país, fecha, temperatura promedio,
              temperatura máxima, temperatura mínima, humedad, velocidad del viento, condición del clima,
              probabilidad de lluvia y otros datos relevantes.
    """
    # Se obtiene la fecha de ayer en formato YYYY-MM-DD
    #   Se utiliza timedelta para restar un día a la fecha actual
    #   y se formatea la fecha en el formato requerido por la API
    # NOTA: Se usa el clima de ayer para asegurar que los datos sean consistentes y no dependan de la hora actual
    yesterday = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    # Se define el parámetro de la solicitud a la API, 
    #   incluyendo la clave de API, la ciudad y la fecha
    params = {
        "key": API_KEY,
        "q": CITY,
        "dt": yesterday
    }

    # Se realiza la solicitud a la API y se maneja cualquier error de conexión
    try:
        # Se realiza la solicitud GET a la API de WeatherAPI con los parámetros definidos
        response = requests.get(BASE_URL, params=params)
        # Se verifica si la respuesta es exitosa (código 200)
        #   Si no es exitosa, se lanza una excepción
        response.raise_for_status()
        # Se convierte la respuesta JSON en un diccionario de Python
        #   y se almacena en la variable data
        data = response.json()

    # Se maneja cualquier error de conexión o respuesta no exitosa 
    except requests.exceptions.RequestException as e:
        print(f"ERROR | No se pudo obtener datos de la API de WeatherAPI: {e}")
        return None
    
    # Se extrae la información relevante del clima de la respuesta JSON
    weather_info = extract_weather_info(data)
    
    # Retorna un diccionario con la información del clima
    return weather_info


def extract_weather_info(data):
    """
    Extrae información relevante del JSON de respuesta de la API de WeatherAPI.

    Args:
        data: JSON de respuesta de la API
    
    Returns:
        dict: Diccionario con los datos extraídos

    Raises:
        Exception: Si hay un error al extraer los datos
    """
    try:
        location_data = data["location"]                            # Información de la ubicación
        weather_data = data["forecast"]["forecastday"][0]["day"]    # Información del clima
        report_date = data["forecast"]["forecastday"][0]["date"]    # Fecha del reporte

        return {
            "country": location_data["country"],                        # País
            "date": report_date,                                        # Fecha del reporte
            "avg_temp_c": weather_data["avgtemp_c"],                    # Temperatura promedio en °C
            "max_temp_c": weather_data["maxtemp_c"],                    # Temperatura máxima en °C
            "min_temp_c": weather_data["mintemp_c"],                    # Temperatura mínima en °C
            "humidity": weather_data["avghumidity"],                    # Humedad promedio
            "wind_kph": weather_data["maxwind_kph"],                    # Velocidad máxima del viento en km/h
            "condition": weather_data["condition"]["text"],             # Condición del clima
            "chance_of_rain": weather_data["daily_chance_of_rain"],     # Probabilidad de lluvia
            "will_it_rain": weather_data["daily_will_it_rain"],         # ¿Lloverá?
            "totalprecip_mm": weather_data["totalprecip_mm"],           # Precipitación total en mm
            "uv": weather_data["uv"]
        }
    
    except Exception as e:
        # Si hay un error al extraer los datos, se lanza una excepción
        print(f"ERROR | Mala extracción de datos: {e}")
        return None
    

def update_local_csv(new_row):
    """
    Actualiza el archivo CSV local con la nueva fila de datos del clima.
    Si el archivo CSV no existe, se crea uno nuevo. Si ya existe, se agrega la nueva fila.

    Args:
        new_row (dict): Nueva fila de datos del clima

    Returns:
        None

    Raises:
        Exception: Si hay un error al actualizar el archivo CSV o si la fecha ya existe en el CSV
    """
    # Se define la ruta del archivo CSV local
    file_path = "/opt/airflow/data/weather_data.csv"
    try:
        # Leer fechas existentes en el CSV
        existing_dates = set()
        if os.path.exists(file_path):
            with open(file_path, "r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_dates.add(row["date"])
        
        # Verificar si la fecha ya existe en el CSV
        if new_row.get("date") in existing_dates:
            raise(f"Registro del: {new_row.get('date')} ya existe en el CSV.")
    
        # Guardar los datos en el CSV
        with open(file_path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=new_row.keys())
            writer.writerow(new_row)
        
        print(f"SUCCESS | Registro guardado el: {new_row.get('date')} en: {file_path}")
    
    except Exception as e:
        print(f"ERROR | Actualizacion fallida: {e}")