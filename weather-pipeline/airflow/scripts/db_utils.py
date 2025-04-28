# Modulo para manejar la conexión a la base de datos PostgreSQL y la inserción de datos desde un CSV

# --- Librerías ---
# Conexión a PostgreSQL
import psycopg2 
# Manejo de datos
import pandas as pd

# --- Funciones ---


def get_postgres_connection():
    """
    Establece una conexión a la base de datos PostgreSQL.
    
    Args:
        None
    
    Returns:
        conn: psycopg2 connection object
    """
    # Crear la conexión a la base de datos PostgreSQL
    db_conn = psycopg2.connect(
        host="postgres",    # nombre del servicio en docker-compose
        database="airflow", # nombre de la base de datos
        user="airflow",     # nombre de usuario
        password="airflow", # contraseña
        port=5432           # puerto por defecto de PostgreSQL
    )
    # Retornar la conexión
    return db_conn


def create_weather_table():
    """
    Crea la tabla weather_data en la base de datos PostgreSQL si no existe. 

    Args:
        None

    Returns:
        None
    """
    # Definición de la consulta SQL para crear la tabla
    # Si la tabla ya existe, no se crea de nuevo
    create_table_query = """
    CREATE TABLE IF NOT EXISTS weather_data (
        id SERIAL PRIMARY KEY,
        country VARCHAR(100),
        date DATE,
        avg_temp_c FLOAT,
        max_temp_c FLOAT,
        min_temp_c FLOAT,
        humidity INTEGER,
        wind_kph FLOAT,
        condition VARCHAR(100),
        chance_of_rain INTEGER,
        will_it_rain INTEGER,
        totalprecip_mm FLOAT,
        uv FLOAT
    );
    """
    # Obtener la conexión a la base de datos
    conn = get_postgres_connection()
    # Crear un cursor para ejecutar la consulta
    cursor = conn.cursor()
    # Ejecutar la consulta para crear la tabla
    cursor.execute(create_table_query)
    # Confirmar los cambios en la base de datos
    conn.commit()
    # Cerrar el cursor y la conexión
    cursor.close()
    # Cerrar la conexión a la base de datos
    conn.close()
    # Mensaje de confirmación
    print("SUCCESS: Tabla weather_data creada o verificada.")


def validate_row(row):
    """
    Valida una fila del DataFrame para asegurarse de que contiene datos válidos.
    Si la fila no es válida, se omite al insertar en la base de datos.

    Args:
        row (pd.Series): Fila del DataFrame a validar.

    Returns:
        bool: True si la fila es válida, False si no lo es.

    Raises:
        Exception: Si ocurre un error durante la validación.
    """
    try:
        # Validacion de los datos de la fila
        #   Verifica si los campos obligatorios están presentes y no son nulos
        #   y si los valores son del tipo correcto
        
        # Si el país es nulo o vacío, se omite la fila
        if pd.isna(row['country']) or str(row['country']).strip() == "":
            return False
        
        # Si la fecha es nula o no es una fecha válida, se omite la fila
        if pd.isna(row['date']) or not pd.to_datetime(row['date'], errors='coerce'):
            return False
        
        # Si los valores de temperatura, humedad, viento, etc. son nulos se omite la fila
        if any(pd.isna(row[col]) for col in [
            'avg_temp_c', 'max_temp_c', 'min_temp_c', 'humidity', 
            'wind_kph', 'condition', 'chance_of_rain', 'will_it_rain', 
            'totalprecip_mm', 'uv']):
            return False
        
        # Si los valores de humedad, probabilidad de lluvia, etc. están fuera de rango, se omite la fila
        if not (0 <= row['humidity'] <= 100):
            return False
        if not (0 <= row['chance_of_rain'] <= 100):
            return False
        
        # Si la probabilidad de lluvia no es 0 o 1 (booleano), se omite la fila
        if not (row['will_it_rain'] in [0, 1]):
            return False
        
        # Si la velocidad del viento es negativa, se omite la fila
        if row['wind_kph'] < 0:
            return False
        
        # Si la temperatura promedio, máxima o mínima están fuera de rango, se omite la fila
        #   Las temperaturas están en grados Celsius y se validan entre -100 y 100
        if row['avg_temp_c'] < -100 or row['avg_temp_c'] > 100:
            return False
        if row['max_temp_c'] < -100 or row['max_temp_c'] > 100:
            return False
        if row['min_temp_c'] < -100 or row['min_temp_c'] > 100:
            return False
        
        # Si la precipitación total es negativa, se omite la fila
        if row['totalprecip_mm'] < 0:
            return False
        
        # Si el índice UV es negativo o mayor a 11, se omite la fila
        #   El índice UV generalmente varía entre 0 y 10, aunque puede ser mayor en condiciones extremas
        #   pero se considera que un índice UV de 11 es poco común pues es extremadamente alto.
        if not (0 <= row['uv'] <= 11):
            return False
        
        # Si todos los chequeos pasan, la fila es válida
        #   Se puede agregar más validaciones según sea necesario
        return True
        
    except Exception as e:
        print(f"ERROR | fallo en la validación de la fila: {e}")
        return False  # Si algo falla, se descarta la fila


def insert_weather_data(file_path="/opt/airflow/data/weather_data.csv"):
    """
    Inserta datos de un archivo CSV en la tabla weather_data de PostgreSQL.

    Valida cada fila antes de la inserción. Si la fila no es válida, se omite.
    Si la fila ya existe en la base de datos, se omite la inserción.

    Args:
        file_path (str): Ruta del archivo CSV que contiene los datos de clima. (default: "/opt/airflow/data/weather_data.csv")

    Returns:
        None

    Raises:
        Exception: Si ocurre un error durante la inserción de datos.
    """
    # Leer el archivo CSV en un DataFrame de pandas
    df = pd.read_csv(file_path)

    # Obtener la conexión a la base de datos
    #   y crear un cursor para ejecutar las consultas
    conn = get_postgres_connection()
    cursor = conn.cursor()

    # Contadores para filas insertadas y omitidas
    inserted_rows = 0
    skipped_rows = 0

    # Iterar sobre cada fila del DataFrame
    for index, row in df.iterrows():
        # Validar la fila antes de la inserción
        if validate_row(row):
            # Si la fila es válida, preparar la consulta de inserción
            #   y ejecutar la consulta
            insert_query = """
            INSERT INTO weather_data (country, date, avg_temp_c, max_temp_c, min_temp_c,
                                      humidity, wind_kph, condition, chance_of_rain,
                                      will_it_rain, totalprecip_mm, uv)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
            """
            # Ejecutar la consulta de inserción con los valores de la fila
            #   Se utiliza ON CONFLICT para evitar duplicados
            cursor.execute(insert_query, (
                row['country'],
                row['date'],
                row['avg_temp_c'],
                row['max_temp_c'],
                row['min_temp_c'],
                row['humidity'],
                row['wind_kph'],
                row['condition'],
                row['chance_of_rain'],
                row['will_it_rain'],
                row['totalprecip_mm'],
                row['uv'],
            ))
            # Incrementar el contador de filas insertadas
            inserted_rows += 1
        else:
            # Si la fila no es válida, incrementar el contador de filas omitidas
            skipped_rows += 1

    # Confirmar los cambios en la base de datos
    conn.commit()

    # Cerrar el cursor y la conexión a la base de datos
    cursor.close()
    conn.close()

    # Mensaje de confirmación
    print(f"SUCCESS | Datos insertados exitosamente: {inserted_rows}")
    print(f"INFO | Datos omitidos por validación: {skipped_rows}")
