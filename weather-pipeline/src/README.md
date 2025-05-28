# ⚙️ Scripts Generales de Preparación

## 📝 Descripción

Este directorio incluye scripts utilitarios que deben ejecutarse una sola vez (o de forma puntual) como parte del setup inicial o de mantenimiento del entorno del proyecto. Son independientes de los DAGs y la aplicación web.

## 📑 Tabla de Contenidos

- [📝 Descripción](#-descripción)
- [📦 Scripts Incluidos](#-scripts-incluidos)
  - [`dataset_creator.py`](#dataset_creatorpy)
  - [`gen_fernet_key.py`](#gen_fernet_keypy)
  - [`requirements.txt`](#requirementstxt)

## 📦 Scripts Incluidos

### `dataset_creator.py`

Este script consulta la API de [WeatherAPI](https://www.weatherapi.com/) y construye un archivo `weather_data.csv` con datos climáticos históricos diarios para la ciudad de Guatemala.

- Rango de fechas configurable (`START_DATE` y `END_DATE`).
- Omite duplicados si el archivo CSV ya contiene una fecha.
- Realiza reintentos automáticos en caso de fallos de conexión.
- El archivo se guarda en `../../airflow/data/weather_data.csv`.

> [!IMPORTANT]
> Este script se usa para generar datos históricos antes de iniciar la ejecución regular del pipeline en Airflow.

### `gen_fernet_key.py`

Script para generar y guardar una **clave Fernet** necesaria para que Apache Airflow encripte conexiones y variables.

- Crea una clave con `cryptography.Fernet`.
- Detecta si ya existe una clave `AIRFLOW__CORE__FERNET_KEY` en el archivo `.env`.
- Permite sobrescribirla o agregarla si no existe.
- El archivo `.env` objetivo se asume en la raíz del proyecto (`../../.env` desde este script).

### `requirements.txt`

Este archivo incluye las dependencias necesarias para ejecutar estos scripts:

```txt
python-dotenv      # Cargar variables del archivo .env
cryptography       # Para generar claves Fernet
requests           # Para llamadas HTTP a WeatherAPI
```
