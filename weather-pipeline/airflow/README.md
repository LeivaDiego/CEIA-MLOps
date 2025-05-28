# 🌬️ Airflow – Orquestación de Weather Pipeline

Este directorio contiene toda la configuración necesaria para la ejecución de flujos de trabajo automatizados con **Apache Airflow** dentro del proyecto **Weather Pipeline**.

Airflow se encarga de orquestar el procesamiento de datos meteorológicos, el entrenamiento y monitoreo del modelo de predicción de lluvia, así como la ingestión y limpieza de datos históricos desde APIs externas.

## 📑 Tabla de Contenidos

- [📑 Tabla de Contenidos](#-tabla-de-contenidos)
- [📁 Estructura](#-estructura)
- [⚙️ Funcionalidad General](#️-funcionalidad-general)
- [🔗 Recursos Detallados](#-recursos-detallados)
- [🧩 Dependencias](#-dependencias)
- [🔐 Variables Iniciales](#-variables-iniciales)
- [📌 Notas](#-notas)

## 📁 Estructura

```text
airflow/
├── dags/                # Flujos de trabajo definidos como DAGs (ver README en la carpeta)
├── data/                # Dataset CSV base generado previamente
├── logs/                # Carpeta requerida para almacenar logs de ejecución
├── pgadmin/             # Configuración opcional para cliente pgAdmin
├── scripts/             # Funciones auxiliares utilizadas en los DAGs (ver README en la carpeta)
├── Dockerfile           # Imagen extendida de Airflow con dependencias personalizadas
├── requirements.txt     # Librerías necesarias para los DAGs y scripts
└── variables.json       # Variables de entorno iniciales para Airflow (ej. API KEY)
```

## ⚙️ Funcionalidad General

Airflow se utiliza para automatizar las siguientes tareas del sistema:

* 📥 Ingesta de datos históricos desde la API del clima.
* 🧼 Limpieza y validación de datos antes de ser guardados en PostgreSQL.
* 🧠 Entrenamiento periódico de modelos predictivos.
* 📈 Monitoreo del rendimiento del modelo y alertas si pierde precisión.
* ♻️ Retraining programado basado en ventanas de tiempo configurables.

## 🔗 Recursos Detallados

* **[`dags/`](./dags/README.md)** – Aquí encontrarás los DAGs (flujos de trabajo) disponibles y sus descripciones paso a paso.
* **[`scripts/`](./scripts/README.md)** – Contiene módulos auxiliares reutilizados por los DAGs (manejo de base de datos, validaciones, modelo, logs, etc.).

## 🧩 Dependencias

Las dependencias necesarias para la ejecución de los DAGs y scripts están listadas en:

```bash
airflow/requirements.txt
```

Estas se instalan automáticamente al construir la imagen Docker de Airflow.

## 🔐 Variables Iniciales

Las variables necesarias para la ejecución (como la clave de la Weather API) deben declararse en `airflow/variables.json` y se cargarán automáticamente al ejecutar:

```bash
docker compose up airflow-init
```

## 📌 Notas

* Recuerda crear manualmente la carpeta `airflow/logs/` antes de ejecutar los servicios.
* Puedes usar `pgAdmin` (contenedor opcional) para observar la base de datos en tiempo real.
