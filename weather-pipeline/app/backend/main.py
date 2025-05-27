# --- Librerías ---
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
import joblib
import pandas as pd
import logging
import os

# --- Configuración ---
# Inicializa la aplicación FastAPI
app = FastAPI()

# --- Configuración del logger ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Servir archivos estáticos
# 
#  desde /app/frontend
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

# Sirve el archivo HTML principal en la raíz
@app.get("/")
def root():
    return FileResponse("/app/frontend/index.html")


# Endpoint de salud para verificar que la API está funcionando
@app.get("/health")
def health_check():
    return {"status": "ok"}


# Endpoint para predicciones con el modelo más reciente válido
@app.get("/predict")
def predict(temp: float, humidity: int, wind: float):
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"]
        )
        cur = conn.cursor()
        logger.info("Conexión a la base de datos PostgreSQL exitosa.")

        # Obtener el path del modelo válido más reciente
        cur.execute("""
            SELECT model_path
            FROM model_metrics
            WHERE is_valid = TRUE
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        row = cur.fetchone()
        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()

        # Validar que se haya encontrado un modelo válido
        if not row:
            logger.error("No se encontraron modelos válidos en la base de datos.")
            raise HTTPException(status_code=404, detail="No hay modelos válidos registrados en la base de datos.")

        model_path = row[0]
        logger.info(f"Modelo válido encontrado: {model_path}")

        # Transformar la ruta de Airflow a la del contenedor actual
        if model_path.startswith("/opt/airflow/models/"):
            model_path = model_path.replace("/opt/airflow/models/", "/app/models/")

        logger.info(f"Ruta corregida del modelo en weather-app: {model_path}")

        # Validar existencia del archivo .pkl
        if not os.path.exists(model_path):
            logger.error(f"El archivo del modelo no se encontró en {model_path}")
            raise HTTPException(status_code=500, detail=f"El archivo del modelo no disponible.")

        # Cargar el modelo y predecir
        logger.info("Cargando el modelo...")
        model = joblib.load(model_path)
        features_df = pd.DataFrame(
             [[temp, humidity, wind]],
             columns=["avg_temp_c", "humidity", "wind_kph"]
            )
        logger.info(f"Input para predicción:\n{features_df}")
        prediction = model.predict(features_df)

        logger.info(f"Predicción realizada: {prediction}")

        return {
            "will_it_rain": int(prediction[0])
        }

    except HTTPException as he:
        raise he
    
    except Exception as e:
        logger.error(f"Error inesperado en /predict.")
        raise HTTPException(status_code=500, detail="Error interno al generar la predicción: " + str(e))


# Endpoint para datos históricos de temperatura
@app.get("/metrics/temperature")
def get_temperature_metrics():
    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"]
        )

        # Obtener datos de temperatura promedio 
        cur = conn.cursor()
        cur.execute("SELECT date, avg_temp_c FROM weather_data ORDER BY date;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # Formatear los resultados
        dates = [str(row[0]) for row in rows]
        temps = [row[1] for row in rows]


        return {
            "dates": dates,
            "avg_temp": temps
        }
    
    # Si hay un error al conectar a la base de datos o al ejecutar la consulta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
