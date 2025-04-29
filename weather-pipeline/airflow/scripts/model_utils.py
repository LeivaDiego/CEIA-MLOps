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

# --- Funciones ---

def load_data_from_postgres():
    """
    Carga todos los datos históricos desde la tabla weather_data en PostgreSQL.

    Returns:
        pd.DataFrame: Datos del clima.
    """
    conn = get_postgres_connection()
    query = "SELECT * FROM weather_data;"
    df = pd.read_sql(query, conn)
    conn.close()
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
    df = df.copy()
    df = df.drop(columns=["id", "country", "condition"], errors="ignore")

    X = df.drop(columns=["will_it_rain"])
    y = df["will_it_rain"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

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
    model = get_base_model()
    model.fit(X_train, y_train)
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
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1_score": f1_score(y_test, y_pred, zero_division=0)
    }
    return metrics


def save_model(model, path):
    """
    Guarda el modelo entrenado en disco como archivo .pkl.

    Args:
        model: Modelo entrenado.
        path (str): Ruta donde guardar el modelo.
    """
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
    with open(path, "rb") as f:
        model = pickle.load(f)
    print(f"SUCCESS | Modelo cargado desde {path}")
    return model


def save_metrics_to_db(metrics, model_version, date_trained):
    """
    Guarda las métricas de desempeño del modelo en la tabla de métricas en PostgreSQL.

    Args:
        metrics (dict): Diccionario de métricas.
        model_version (str): Versión o nombre del modelo.
        date_trained (str): Fecha de entrenamiento.
    """
    conn = get_postgres_connection()
    cursor = conn.cursor()

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
    cursor.execute(create_table_query)

    insert_query = """
    INSERT INTO model_metrics (model_version, date_trained, accuracy, precision, recall, f1_score)
    VALUES (%s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, (
        model_version,
        date_trained,
        metrics["accuracy"],
        metrics["precision"],
        metrics["recall"],
        metrics["f1_score"]
    ))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"SUCCESS | Métricas guardadas en base de datos para modelo {model_version}")