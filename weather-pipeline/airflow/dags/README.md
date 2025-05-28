# ☁️ DAGs del Proyecto de Predicción Climática

## 📝 Descripción

Esta carpeta contiene DAGs avanzados de Apache Airflow diseñados para automatizar el flujo de trabajo de un sistema de predicción de lluvia. Los DAGs abarcan desde la **ingesta de datos climáticos** y la **inicialización de la base de datos**, hasta el **entrenamiento de modelos de ML** y su **monitoreo periódico**.

## 📑 Tabla de Contenidos

* [📝 Descripción](#-descripción)
* [📦 DAGs Incluidos](#-dags-incluidos)
  * [1. `data_ingestion_dag`](#1-data_ingestion_dag)
  * [2. `database_bootstrap_dag`](#2-database_bootstrap_dag)
  * [3. `model_training_dag`](#3-model_training_dag)
  * [4. `model_monitoring_dag`](#4-model_monitoring_dag)

## 📦 DAGs Incluidos

### 1. `data_ingestion_dag`

**Archivo:** `data_ingestion_dag.py`
**Programación:** Diaria (`@daily`)
**Tags:** `ingestion`, `weatherapi`

Este DAG realiza la ingesta diaria de datos de clima desde la API de [WeatherAPI](https://www.weatherapi.com/), valida los datos, los almacena en PostgreSQL y actualiza un archivo CSV local.

#### Flujo de tareas

1. **`fetch_weather_data`**
   Consulta la API y guarda los datos en XCom.

2. **`validate_and_clean_data`**
   Valida el formato y consistencia de los datos.

3. **`insert_into_postgres`**
   Inserta los datos validados en la base de datos.

4. **`update_local_csv`**
   Actualiza un archivo CSV local para respaldo.

### 2. `database_bootstrap_dag`

**Archivo:** `db_bootstrap_dag.py`
**Programación:** Manual (sin schedule)
**Tags:** `bootstrap`, `database`

Este DAG se ejecuta una vez para preparar la base de datos al inicio del proyecto, creando las tablas necesarias y cargando datos históricos.

#### Flujo de tareas

1. **`create_weather_table`**
   Crea la tabla principal de clima.

2. **`create_log_table`**
   Crea la tabla para registrar errores de validación.

3. **`create_metrics_table`**
   Crea la tabla para almacenar métricas de modelos.

4. **`insert_weather_data`**
   Inserta datos históricos de clima.

### 3. `model_training_dag`

**Archivo:** `model_training_dag.py`
**Programación:** Mensual (`@monthly`)
**Tags:** `training`, `ml`, `weather`

Este DAG entrena un modelo de predicción de lluvia basado en los datos históricos almacenados. Al final, guarda las métricas y dispara automáticamente el DAG de monitoreo.

#### Flujo de tareas

1. **`load_and_preprocess_data`**
   Carga y divide los datos desde PostgreSQL.

2. **`train_model`**
   Entrena un modelo de clasificación y lo guarda como `.pkl`.

3. **`evaluate_model`**
   Evalúa el modelo y guarda las métricas en XCom.

4. **`save_model_and_metrics`**
   Registra el modelo y las métricas en la base de datos.

5. **`trigger_model_monitoring_dag`**
   Dispara el DAG de monitoreo para comparar el modelo actual con el anterior.

### 4. `model_monitoring_dag`

**Archivo:** `model_monitoring_dag.py`
**Programación:** Trigger manual (se ejecuta desde `model_training_dag`)
**Tags:** `model`, `monitoring`

Este DAG se encarga de comparar el nuevo modelo entrenado con el anterior y verificar si hubo mejoras. Es útil para evitar regresiones en el rendimiento del modelo.

#### Tarea principal

* **`compare_latest_models`**

  Carga los dos modelos más recientes y compara sus métricas.
