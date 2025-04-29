# Modulo para preparar el modelo de predicción de lluvia, junto con las métricas de desempeño y su almacenamiento en PostgreSQL.

# --- Librerías ---
# Manejo de datos
import pandas as pd
import pickle
# Scikit-learn para el modelo y métricas 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# PostgreSQL para conexión y almacenamiento de métricas
from scripts.db_utils import get_postgres_connection
from scripts.base_model import get_base_model
# Manejo de archivos
import os


# --- Funciones ---

def load_data_from_postgres():
    """
    Carga todos los datos históricos desde la tabla weather_data en PostgreSQL.

    Args:
        None

    Returns:
        pd.DataFrame: Datos del clima.
    """
    # Conexión a PostgreSQL
    conn = get_postgres_connection()
    # Consulta SQL para obtener todos los datos de la tabla weather_data
    query = "SELECT * FROM weather_data;"
    # Ejecuta la consulta y carga los datos en un DataFrame de pandas
    df = pd.read_sql(query, conn)
    # Cierra la conexión a la base de datos
    conn.close()
    # retorna el DataFrame con los datos
    return df


def preprocess_data(df, test_size=0.2, random_state=42):
    """
    Preprocesa el DataFrame de datos históricos y realiza un split en train/test.

    Args:
        df (pd.DataFrame): Datos del clima.
        test_size (float): Proporción para el conjunto de prueba. Default 20%.
        random_state (int): Semilla para replicabilidad.

    Returns:
        X_train (pd.DataFrame): Features para entrenamiento.
        X_test (pd.DataFrame): Features para prueba.
        y_train (pd.Series): Target para entrenamiento.
        y_test (pd.Series): Target para prueba.
    """
    # Copia el DataFrame y elimina columnas innecesarias 
    df = df.copy()
    df = df.drop(columns=["id", "country", "condition"], errors="ignore")
    # Se divide el DataFrame en características (X) y target (y)
    X = df.drop(columns=["will_it_rain"])
    y = df["will_it_rain"]

    # Se hace un split de los datos en conjuntos de entrenamiento y prueba
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    # retorna los conjuntos de datos preprocesados y divididos
    return X_train, X_test, y_train, y_test



def train_model(X_train, y_train):
    """
    Entrena un modelo base usando los datos proporcionados.

    Args:
        X_train (pd.DataFrame): Features para entrenamiento.
        y_train (pd.Series): Etiquetas para entrenamiento.

    Returns:
        model: Modelo entrenado.
    """
    # Crea el modelo base de Random Forest
    model = get_base_model()
    # Entrena el modelo con los datos de entrenamiento
    model.fit(X_train, y_train)
    # retorna el modelo entrenado
    return model


def evaluate_model(model, X_test, y_test):
    """
    Evalúa el modelo en datos de prueba y calcula métricas.

    Args:
        model: Modelo entrenado.
        X_test (pd.DataFrame): Features de prueba.
        y_test (pd.Series): Etiquetas de prueba.

    Returns:
        dict: Diccionario de métricas.
    """
    # Realiza predicciones con el modelo en los datos de prueba
    y_pred = model.predict(X_test)

    # Calcula las métricas de desempeño del modelo
    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0)
    }
    # Retorna un diccionario con las métricas calculadas
    return metrics


def save_model(model, path):
    """
    Guarda el modelo entrenado en disco como archivo .pkl.

    Args:
        model: Modelo entrenado.
        path (str): Ruta donde guardar el modelo.

    Returns:
        None
    """
    # Guarda el modelo en un archivo .pkl usando pickle
    with open(path, "wb") as f:
        pickle.dump(model, f)
    print(f"SUCCESS | Modelo guardado en {path}")


def load_latest_model(path):
    """
    Carga el modelo más reciente desde disco.

    Args:
        path (str): Ruta del archivo .pkl

    Returns:
        model: Modelo cargado.
    """
    # Carga el modelo desde el archivo .pkl usando pickle
    with open(path, "rb") as f:
        model = pickle.load(f)
    print(f"SUCCESS | Modelo cargado desde {path}")
    # retorna el modelo cargado
    return model


def save_metrics_to_db(metrics, model_version, date_trained):
    """
    Guarda las métricas de desempeño del modelo en la tabla de métricas en PostgreSQL.

    Args:
        metrics (dict): Diccionario de métricas.
        model_version (str): Versión o nombre del modelo.
        date_trained (str): Fecha de entrenamiento.

    Returns:
        None
    """
    # Conexión a PostgreSQL
    conn = get_postgres_connection()
    cursor = conn.cursor()

    # Crea la tabla si no existe
    create_table_query = """
    CREATE TABLE IF NOT EXISTS model_metrics (
        id SERIAL PRIMARY KEY,
        model_version VARCHAR(100),
        date_trained DATE,
        accuracy FLOAT,
        precision FLOAT,
        recall FLOAT,
        f1_score FLOAT
    );
    """
    # Ejecuta la consulta para crear la tabla
    cursor.execute(create_table_query)

    # Inserta las métricas en la tabla
    insert_query = """
    INSERT INTO model_metrics (model_version, date_trained, accuracy, precision, recall, f1_score)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    # Ejecuta la consulta de inserción con las métricas
    cursor.execute(insert_query, (
        model_version,
        date_trained,
        metrics["accuracy"],
        metrics["precision"],
        metrics["recall"],
        metrics["f1_score"]
    ))

    # Confirma los cambios y cierra la conexión
    conn.commit()
    cursor.close()
    conn.close()
    # Imprime un mensaje de éxito
    print(f"SUCCESS | Métricas guardadas en base de datos para modelo {model_version}")


def get_next_model_version(models_dir="/opt/airflow/models/"):
    """
    Obtiene el próximo número de versión de modelo basado en los archivos existentes.

    Args:
        models_dir (str): Directorio donde se almacenan los modelos .pkl

    Returns:
        str: Nueva versión del modelo, por ejemplo: 'v3'
    """
    # Verifica si el directorio de modelos existe, si no, lo crea y retorna "v1"
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        return "v1"
    
    # Lista todos los archivos en el directorio de modelos que terminan con .pkl
    model_files = [f for f in os.listdir(models_dir) if f.endswith(".pkl")]
    version_numbers = []

    # Itera sobre los archivos y extrae los números de versión
    # Filtra los nombres que comienzan con "model_v" y extrae el número de versión
    for f in model_files:
        name = os.path.splitext(f)[0]  # quita .pkl
        if name.startswith("model_v"):
            try:
                num = int(name.replace("model_v", ""))
                version_numbers.append(num)
            except ValueError:
                continue
            
    # Si no hay números de versión, retorna "v1", de lo contrario, retorna la próxima versión
    if not version_numbers:
        return "v1"
    else:
        return f"v{max(version_numbers) + 1}"
