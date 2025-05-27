# Modulo para preparar el modelo de predicción de lluvia, junto con las métricas de desempeño y su almacenamiento en PostgreSQL.

# --- Librerías ---
# Manejo de rutas y configuración
#   de ruta de modulo
import sys
import os
sys.path.append('/opt/airflow/scripts')
# Manejo de datos
import pandas as pd
import pickle
# Scikit-learn para el modelo y métricas 
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
# PostgreSQL para conexión y almacenamiento de métricas
from db_utils import get_postgres_connection
from base_model import get_base_model


# --- Configuración del logger ---
# Se importa el logger desde el módulo de utilidades de logging
from log_utils import get_logger
logger = get_logger(__name__)


# --- Funciones ---

def load_data_from_postgres():
    """
    Carga todos los datos históricos desde la tabla weather_data en PostgreSQL.

    Args:
        None

    Returns:
        pd.DataFrame: Datos del clima.
    """
    try:
        # Conexión a PostgreSQL
        conn = get_postgres_connection()
        # Consulta SQL para obtener todos los datos de la tabla weather_data
        query = "SELECT * FROM weather_data;"
        # Ejecuta la consulta y carga los datos en un DataFrame de pandas
        df = pd.read_sql(query, conn)

        if df.empty or df is None:
            logger.warning("La tabla weather_data está vacía.")
            return pd.DataFrame()  # Retorna un DataFrame vacío si no hay datos
        else:
            logger.info(f"Datos cargados desde PostgreSQL exitosamente. Total de registros: {len(df)}")

        # retorna el DataFrame con los datos
        return df
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al cargar datos desde PostgreSQL: {e}")
        return pd.DataFrame()  # Retorna un DataFrame vacío en caso de error
    
    finally:
        # Cierra la conexión a la base de datos
        conn.close()
    
    


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
    try:
        if df.empty or df is None:
            logger.warning("El DataFrame está vacío. No se puede preprocesar.")
            return None, None, None, None

        # Copia el DataFrame y elimina columnas innecesarias 
        df = df.copy()
        df = df.drop(columns=["id", "country", "condition", "date"], errors="ignore")
        
        # Validar que la columna 'will_it_rain' exista en el DataFrame
        if "will_it_rain" not in df.columns:
            logger.error("La columna 'will_it_rain' no existe en el DataFrame.")
            return None, None, None, None
        
        # Se divide el DataFrame en características (X) y target (y)
        X = df.drop(columns=["will_it_rain"])
        # Solo las columnas relevantes para el modelo
        X = df[["avg_temp_c", "humidity", "wind_kph"]]
        y = df["will_it_rain"]

        # Se hace un split de los datos en conjuntos de entrenamiento y prueba
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )

        # Mensaje de éxito
        logger.info(f"Preprocesamiento exitoso: train={len(X_train)}, test={len(X_test)}")

        # Retorna los conjuntos de datos preprocesados y divididos
        return X_train, X_test, y_train, y_test
    
    except ValueError as ve:
        logger.error(f"Error de preprocesamiento: {ve}")
        return None, None, None, None

    except Exception as e:
        logger.error(f"Error inesperado durante preprocesamiento: {e}")
        return None, None, None, None



def train_model(X_train, y_train):
    """
    Entrena un modelo base usando los datos proporcionados.

    Args:
        X_train (pd.DataFrame): Features para entrenamiento.
        y_train (pd.Series): Etiquetas para entrenamiento.

    Returns:
        model: Modelo entrenado.
    """
    try:
        # Validar que los datos de entrenamiento no estén vacíos
        if X_train is None or y_train is None:
            logger.error("Datos de entrenamiento no válidos (None). No se puede entrenar el modelo.")
            return None
        if X_train.empty or y_train.empty:
            logger.error("Datos de entrenamiento vacíos. No se puede entrenar el modelo.")
            return None

        # Crea el modelo base de Random Forest
        model = get_base_model()
        # Entrena el modelo con los datos de entrenamiento
        model.fit(X_train, y_train)
        # Mensaje de éxito
        logger.info("Modelo entrenado exitosamente.")
        # retorna el modelo entrenado
        return model
    
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al entrenar el modelo: {e}")
        return None

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
    # Validar que el modelo y los datos de prueba no estén vacíos
    if model is None:
        logger.error("Modelo no válido (None). No se puede evaluar.")
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None
        }
    
    if X_test is None or y_test is None:
        logger.error("Datos de prueba no válidos (None). No se puede evaluar.")
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None
        }
    
    if X_test.empty or y_test.empty:
        logger.error("Datos de prueba vacíos. No se puede evaluar.")
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None
        }
    
    try:
        # Realiza predicciones con el modelo en los datos de prueba
        y_pred = model.predict(X_test)

        # Calcula las métricas de desempeño del modelo
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, zero_division=0),
            "recall": recall_score(y_test, y_pred, zero_division=0),
            "f1_score": f1_score(y_test, y_pred, zero_division=0)
        }
        # Mensaje de éxito
        logger.info(f"Modelo evaluado exitosamente")

        # Retorna un diccionario con las métricas calculadas
        return metrics
    
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error durante la evaluación del modelo: {e}")
        return {
            "accuracy": None,
            "precision": None,
            "recall": None,
            "f1_score": None
        }


def save_model(model, path):
    """
    Guarda el modelo entrenado en disco como archivo .pkl.

    Args:
        model: Modelo entrenado.
        path (str): Ruta donde guardar el modelo.

    Returns:
        None
    """
    # Verifica si el modelo es válido
    if model is None:
        logger.error("Modelo no válido (None). No se puede guardar.")
        return
    
    # Verifica si la ruta es válida
    if not path or not path.endswith(".pkl"):
        logger.error(f"Ruta no válida para guardar el modelo. Debe ser un archivo .pkl.")
        return
    
    try:
        # Verifica si la carpeta existe, si no, la crea
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Guarda el modelo en un archivo .pkl usando pickle
        with open(path, "wb") as f:
            pickle.dump(model, f)
        # Mensaje de éxito
        logger.info(f"Modelo guardado exitosamente en: {path}")
    
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al guardar el modelo en {path}: {e}")


def load_model(path):
    """
    Carga el modelo más reciente desde disco.

    Args:
        path (str): Ruta del archivo .pkl

    Returns:
        model: Modelo cargado.
    """
    # Verifica si la ruta es válida y si el archivo existe
    if not path or not os.path.exists(path):
        logger.error(f"Ruta no válida o archivo inexistente: {path}")
        return None
    
    try:
        # Carga el modelo desde el archivo .pkl usando pickle
        with open(path, "rb") as f:
            model = pickle.load(f)
        # Mensaje de éxito
        logger.info(f"Modelo cargado exitosamente desde {path}")
        # Retorna el modelo cargado
        return model

    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al cargar el modelo desde {path}: {e}")
        return None


def get_next_model_version(models_dir="/opt/airflow/models/"):
    """
    Obtiene el próximo número de versión de modelo basado en los archivos existentes.

    Args:
        models_dir (str): Directorio donde se almacenan los modelos .pkl

    Returns:
        str: Nueva versión del modelo, por ejemplo: 'v3'
    """
    try:
        # Verifica si el directorio de modelos existe, si no, lo crea y retorna "v1"
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
            logger.info(f"Directorio {models_dir} creado.")
            logger.info("No hay modelos existentes. Retornando versión v1.")
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
                    logger.warning(f"Archivo con formato de versión no reconocido: {f}")
                    continue
            
        # Si no hay números de versión, retorna "v1", de lo contrario, retorna la próxima versión
        if not version_numbers:
            logger.info("No hay versiones de modelo existentes. Retornando versión v1.")
            return "v1"
        
        next_version = max(version_numbers) + 1
        logger.info(f"Versiones de modelo existentes: {version_numbers}. Retornando próxima versión v{next_version}.")
        return f"v{next_version}"

    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al obtener la próxima versión del modelo: {e}")
        return "v1"

def mark_model_as_invalid(model_path):
    """
    Marca un modelo como inválido en la base de datos PostgreSQL.

    Args:
        model_path (str): Ruta del modelo a marcar como inválido.
    """
    try:
        # Conexión a PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Consulta SQL para marcar el modelo como inválido
        update_query = """
        UPDATE model_metrics
        SET is_valid = FALSE
        WHERE model_path = %s;
        """

        # Ejecuta la consulta de actualización
        cursor.execute(update_query, (model_path,))
        # Confirma los cambios en la base de datos
        conn.commit()

        if cursor.rowcount == 0:
            logger.warning(f"No se encontró el modelo en la base de datos: {model_path}")
        else:
            logger.info(f"Modelo {model_path} marcado como inválido en la base de datos.")
    
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error al marcar el modelo como inválido: {e}")
        raise

    finally:
        # Cierra el cursor y la conexión
        cursor.close()
        conn.close()



def compare_models():
    """
    Compara los 2 modelos válidos más recientes.
    Si el nuevo modelo tiene peor F1-score, lo marca como inválido.
    """
    logger.info("Iniciando comparación de modelos válidos más recientes...")

    try:
        # Conexión a PostgreSQL
        conn = get_postgres_connection()
        cursor = conn.cursor()

        # Obtener los 2 modelos válidos más recientes
        cursor.execute("""
            SELECT timestamp, f1_score, model_version, model_path
            FROM model_metrics
            WHERE is_valid = TRUE
            ORDER BY timestamp DESC
            LIMIT 2;
        """)
        rows = cursor.fetchall()

        # Si no hay suficientes modelos válidos, se sale de la función
        if len(rows) < 2:
            logger.warning("No hay suficientes modelos válidos para comparar.")
            return

        # Desempaqueta los resultados
        latest_model = rows[0]
        previous_model = rows[1]

        latest_f1 = latest_model[1]
        previous_f1 = previous_model[1]
        model_path = latest_model[3]

        # Imprime información de los modelos
        logger.info(f"F1-score actual: {latest_f1} | F1-score anterior: {previous_f1}")

        # Compara los F1-scores
        if latest_f1 < previous_f1:
            logger.warning(
                f"Modelo en {model_path} tiene rendimiento inferior (actual: {latest_f1} < anterior: {previous_f1}). Será marcado como inválido."
            )
            mark_model_as_invalid(model_path)
        else:
            logger.info(f"Modelo en {model_path} tiene igual o mejor rendimiento. No se requiere acción.")

        logger.info("Comparación de modelos completada exitosamente.")
    
    except Exception as e:
        # Si ocurre un error, imprime el mensaje de error
        logger.error(f"Error durante la comparación de modelos: {e}")
        raise

    finally:
        # Cierra el cursor y la conexión
        cursor.close()
        conn.close()