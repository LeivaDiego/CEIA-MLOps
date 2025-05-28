import requests
import os
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

# Cargar la API key desde el .env
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")

# Configuración general
CITY = "Guatemala"
START_DATE = datetime(2024, 3, 30)      # Fecha de inicio
END_DATE = datetime(2025, 3, 31)        # Fecha de fin
DATA_DIR = "../../airflow/data"            # Directorio de datos
CSV_FILE = os.path.join(DATA_DIR, "weather_data.csv")   # Archivo CSV de salida
RETRIES = 3
RETRY_DELAY = 5  # segundos

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


# Se hace secuencial debido a que la API no permite hacer un bulk request en la free tier.
def ingest_weather_data(start_date=START_DATE, end_date=END_DATE, data_dir=DATA_DIR):
    """
    Ingesta de datos del clima desde la API de WeatherAPI y guardado en un archivo CSV.
    Se obtienen datos diarios entre las fechas especificadas y se guardan en un archivo CSV.
    Si el archivo CSV ya existe, se omiten las fechas ya registradas para evitar duplicados.
    Se realizan reintentos en caso de errores de conexión o respuesta de la API.

    Args:
        start_date (datetime): Fecha de inicio para la ingesta de datos
        end_date (datetime): Fecha de fin para la ingesta de datos
        data_dir (str): Directorio donde se guardará el archivo CSV

    Returns:
        None

    Raises:
        Exception: Si hay un error en la conexión a la API o al guardar los datos
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"INFO | Directorio creado: {DATA_DIR}")

    # Si ya existe el CSV, leer fechas existentes para no duplicar
    existing_dates = set()
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_dates.add(row["date"])
    else:
        # Si no existe, escribir encabezado
        with open(CSV_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "country", "date", "avg_temp_c", "max_temp_c", "min_temp_c",
                "humidity", "wind_kph", "condition", "chance_of_rain",
                "will_it_rain", "totalprecip_mm", "uv"
            ])
            writer.writeheader()

    # Bucle por fechas
    current_date = START_DATE

    while current_date <= END_DATE:
        date_str = current_date.strftime('%Y-%m-%d')
        # Verificar si la fecha ya existe en el CSV
        if date_str in existing_dates:
            print(f"INFO | Ya existe: {date_str} — saltando.")
            current_date += timedelta(days=1)
            continue
        
        # Si no existe, proceder a obtener los datos
        print(f"INFO | Obteniendo datos para {date_str}...")
        success = False
        attempts = 0

        # Intentar obtener datos de la API con reintentos
        # en caso de errores
        while not success and attempts < RETRIES:
            try:
                # Realizar la solicitud a la API
                # Se utiliza el endpoint de historial para obtener datos pasados
                url = "http://api.weatherapi.com/v1/history.json"
                params = {
                    "key": API_KEY,
                    "q": CITY,
                    "dt": date_str
                }
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                # Obtener información del clima de la respuesta
                row = extract_weather_info(data)

                # Verificar si la fila contiene datos completos
                if row:
                    # Guardar los datos en el CSV
                    with open(CSV_FILE, "a", newline="") as f:
                        writer = csv.DictWriter(f, fieldnames=row.keys())
                        writer.writerow(row)
                    print(f"SUCCESS | Guardado: {date_str}")
                else:
                    raise ValueError("ERROR | Datos incompletos")

                success = True

            except Exception as e:
                attempts += 1
                print(f"ERROR | Intento {attempts} para {date_str}: {e}")
                time.sleep(RETRY_DELAY)

        # Incrementar la fecha
        current_date += timedelta(days=1)

    print("SUCCESS | Ingesta completada.")


if __name__ == "__main__":
    ingest_weather_data()