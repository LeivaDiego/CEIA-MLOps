# --- Librerías ---
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import psycopg2
import joblib
import os

# --- Configuración ---
# Inicializa la aplicación FastAPI
app = FastAPI()

# Servir archivos estáticos
# 
#  desde /app/frontend
app.mount("/static", StaticFiles(directory="/app/frontend"), name="static")

# Sirve el archivo HTML principal en la raíz
@app.get("/")
def root():
    return FileResponse("/app/frontend/index.html")

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

        # Obtener el path del modelo válido más reciente
        cur.execute("""
            SELECT model_path
            FROM model_metrics
            WHERE is_valid = TRUE
            ORDER BY timestamp DESC
            LIMIT 1;
        """)
        row = cur.fetchone()

        cur.close()
        conn.close()

        if not row:
            raise HTTPException(status_code=404, detail="No hay modelos válidos registrados en la base de datos.")

        model_path = row[0]

        # Validar existencia del archivo .pkl
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail=f"El archivo del modelo no se encontró en {model_path}")

        # Cargar el modelo y predecir
        model = joblib.load(model_path)
        features = [[temp, humidity, wind]]
        prediction = model.predict(features)

        return {
            "will_it_rain": int(prediction[0])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Endpoint para datos históricos de temperatura
@app.get("/metrics/temperature")
def get_temperature_metrics():
    try:
        conn = psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASS"]
        )
        cur = conn.cursor()
        cur.execute("SELECT date, avg_temp_c FROM weather_data ORDER BY date;")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        dates = [str(row[0]) for row in rows]
        temps = [row[1] for row in rows]

        return {
            "dates": dates,
            "avg_temp": temps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
