# 🌤️ Weather Insights – Mini App

## 📝 Descripción

**Weather Insights** es una mini aplicación interactiva que permite a los usuarios ingresar datos meteorológicos (temperatura, humedad y viento) para predecir si lloverá, utilizando un modelo de aprendizaje automático entrenado previamente. Además, presenta un gráfico histórico de temperatura promedio con datos obtenidos de una base de datos PostgreSQL.

![Preview de la App](../screenshots/weather-insights-preview.png)

## ⚙️ Estructura General

La app está compuesta por dos partes principales:

1. **🔌 API REST (FastAPI)** – Maneja la lógica de predicción y extracción de métricas.
2. **🖥️ Interfaz Web (HTML + React + Chart.js)** – Permite interactuar con la API y visualizar resultados.

## 🧩 Componentes

### 📁 `/main.py` – API Backend con FastAPI

Este archivo define los siguientes endpoints:

* **`/`**: Sirve el archivo `index.html` desde `/app/frontend`.
* **`/health`**: Verifica si la API está corriendo correctamente.
* **`/predict?temp=&humidity=&wind=`**:

  * Recibe tres parámetros (`float`, `int`, `float`).
  * Carga el modelo válido más reciente desde PostgreSQL.
  * Realiza la predicción y retorna `{"will_it_rain": 0/1}`.
* **`/metrics/temperature`**:

  * Retorna las fechas y temperaturas promedio históricas para graficarlas.

> [!INFO]
> El backend se conecta a PostgreSQL usando variables de entorno (`DB_HOST`, `DB_NAME`, etc.).

### 📁 `/index.html` – Frontend Embebido

Archivo HTML que contiene una mini app hecha con **React** y **Chart.js**, cargados vía CDN.

#### Funciones

* **Formulario de predicción**:

  * El usuario ingresa temperatura, humedad y velocidad del viento.
  * Se realiza una petición GET a `/predict`.
  * El resultado se muestra como:
    `"Sí lloverá ☔"` o `"No lloverá 🌞"`

* **Gráfico de temperatura histórica**:

  * Se consulta `/metrics/temperature`.
  * Se muestra como un gráfico de líneas usando `Chart.js`.

> [!NOTE]
> Puedes reemplazar el gráfico por otros tipos de métricas fácilmente, solo modificando el endpoint.

### 📄 `requirements.txt`

Lista de dependencias para el backend:

```txt
fastapi
uvicorn
psycopg2-binary
joblib
scikit-learn
pandas
```

## 🔁 Interacción entre Componentes

```text
graph TD
    A[Usuario] -->|ingresa datos| B[Frontend React]
    B -->|GET /predict| C[API FastAPI]
    C -->|Carga modelo + predice| D[PostgreSQL + .pkl]
    D --> C
    C -->|Devuelve predicción| B
    B -->|Muestra resultado| A

    B -->|GET /metrics/temperature| C
    C -->|Consulta historial| D
    C -->|Devuelve JSON| B
    B -->|Renderiza gráfico| A
```
