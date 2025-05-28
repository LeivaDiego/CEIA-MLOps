# ⚙️ Scripts Utilitarios para DAGs de Predicción Climática

## 📝 Descripción

Este directorio contiene los módulos que implementan la lógica central utilizada por los DAGs de Apache Airflow del proyecto. Cada archivo encapsula operaciones clave como la conexión a base de datos, la consulta a APIs externas, la validación de datos, el entrenamiento de modelos y el registro de logs. Estos scripts **no deben ejecutarse de forma directa**, ya que están diseñados para ser invocados desde DAGs.

## 📑 Tabla de Contenidos

* [📝 Descripción](#-descripción)
* [📑 Tabla de Contenidos](#-tabla-de-contenidos)
* [📦 Módulos Incluidos](#-módulos-incluidos)
  * [📡 Integración con WeatherAPI](#-integración-con-weatherapi)
  * [🧠 Modelo Base de ML](#-modelo-base-de-ml)
  * [🗄️ Utilidades de Base de Datos](#️-utilidades-de-base-de-datos)
  * [🪵 Configuración de Logging](#-configuración-de-logging)
  * [🤖 Entrenamiento, Evaluación y Comparación de Modelos](#-entrenamiento-evaluación-y-comparación-de-modelos)

## 📦 Módulos Incluidos

### 📡 Integración con WeatherAPI

**Archivo:** `api_utils.py`

Contiene funciones que gestionan la consulta a la API de [WeatherAPI.com](https://www.weatherapi.com/) y la actualización de datos en un archivo CSV local.

Funciones clave:

* `fetch_weather_data()`
* `extract_weather_info(data)`
* `update_local_csv(new_row)`

### 🧠 Modelo Base de ML

**Archivo:** `base_model.py`

Define un modelo base de clasificación:

* `get_base_model()`: Instancia un `RandomForestClassifier`.

### 🗄️ Utilidades de Base de Datos

**Archivo:** `db_utils.py`

Funciones para conexión, creación de tablas, validación e inserción en PostgreSQL.

* 🔌 Conexión y creación:

  * `get_postgres_connection()`
  * `create_weather_table()`
  * `create_validation_log_table()`
  * `create_model_metrics_table()`

* 📥 Inserción:

  * `insert_weather_forecast(record)`
  * `insert_history_data(file_path)`

* ✅ Validación:

  * `validate_row(row)`

* 🧾 Registro:

  * `log_validation_error(record, reason)`
  * `log_model_metrics(metrics, model_path, model_version)`

### 🪵 Configuración de Logging

**Archivo:** `log_utils.py`

Logger estándar del proyecto:

* `get_logger(name)`

### 🤖 Entrenamiento, Evaluación y Comparación de Modelos

**Archivo:** `model_utils.py`

Gestiona el ciclo de vida de los modelos de ML.

* 📥 Carga y preprocesamiento:

  * `load_data_from_postgres()`
  * `preprocess_data(df)`

* 🧠 Entrenamiento:

  * `train_model(X_train, y_train)`
  * `evaluate_model(model, X_test, y_test)`

* 💾 Gestión de modelos:

  * `save_model(model, path)`
  * `load_model(path)`
  * `get_next_model_version(models_dir)`
  * `mark_model_as_invalid(model_path)`

* ⚖️ Comparación:

  * `compare_models()`
