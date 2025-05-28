# MLOPS con

![Apache Airflow](https://upload.wikimedia.org/wikipedia/commons/d/de/AirflowLogo.png)

## 📝 Descripción

Este repositorio contiene el progreso y la documentación de mi aprendizaje sobre Apache Airflow durante mis prácticas. El objetivo es crear una guía práctica y útil para nuevos miembros del equipo, proporcionando recursos y ejemplos diseñados específicamente para principiantes que desean experimentar con Apache Airflow en un entorno controlado. Adicionalmente se incluye una app completa de predicción meteorológica con una arquitectura end-to-end que utiliza Airflow, FastAPI, React, PostgreSQL y Docker.

## 📑 Tabla de Contenidos

- [📝 Descripción](#-descripción)
- [🛠️ Pre-requisitos](#️-pre-requisitos)
- [📂 Estructura del Repositorio](#-estructura-del-repositorio)
- [⚡ Guía Rápida (Quickstart)](#-guía-rápida-quickstart)
- [📚 Introducción a MLOps](#-introducción-a-mlops)
- [💡 Siguientes Propuestas](#-siguientes-propuestas)

## 🛠️ Pre-requisitos

- 🐳 Tener Docker y Docker Compose instalados en tu PC. Puedes descargar Docker Desktop (que ya incluye Docker Compose) desde [Docker Desktop](https://www.docker.com/products/docker-desktop) y seguir las instrucciones de instalación según tu sistema operativo.

## 📂 Estructura del Repositorio

```text
workspace/
├─ quickstart-airflow/         # Entorno base para aprender Airflow paso a paso
├─ intro-mlops/                # Conceptos y buenas prácticas de MLOps
├─ weather-pipeline/           # Proyecto completo de predicción meteorológica con MLOps
└─ README.md                   # Este archivo
```

## ⚡ Guía Rápida (Quickstart)

Para una guía detallada sobre cómo iniciar con Apache Airflow en Windows utilizando Docker, dirígete a la carpeta `quickstart-airflow` y sigue las instrucciones en su README correspondiente.

```bash
cd workspace/quickstart-airflow
cat README.md
```

## 📚 Introducción a MLOps

La carpeta `intro-mlops` contiene un información detallada con los conceptos básicos de MLOps, incluyendo:

- **¿Qué es MLOps?** Definición y objetivos.
- **Arquitecturas comunes en MLOps.** Tipos de flujos de trabajo y arquitecturas recomendadas.
- **Herramientas y Tecnologías.** Desde el desarrollo de modelos hasta su monitoreo en producción.
- **Buenas Prácticas.** Cómo asegurar un flujo de trabajo eficiente y seguro.

Para más detalles, dirígete a la carpeta `intro-mlops` y lee el contenido de su `README.md` correspondiente.

```bash
cd workspace/intro-mlops
cat README.md
```

## ☁️ Weather Pipeline (Proyecto Completo)

El corazón práctico de este repositorio es el proyecto [`weather-pipeline`](./weather-pipeline), una solución end-to-end con las siguientes características:

### Tecnologías Integradas

- **Airflow** – Para la orquestación del flujo de datos y entrenamientos programados.
- **FastAPI + React** – Para una interfaz de usuario ligera pero funcional.
- **PostgreSQL** – Como sistema de almacenamiento central.
- **pgAdmin** – Herramienta opcional para explorar la base de datos.
- **Docker** – Todo corre en contenedores, lo que permite una configuración reproducible.

### Funcionalidades Destacadas

- Ingesta y validación de datos climáticos.
- Entrenamiento automático de modelos.
- Predicción de lluvia desde la interfaz web.
- Monitoreo del desempeño del modelo con alertas.

### Para comenzar

```bash
cd workspace/weather-pipeline
```

Luego, sigue los pasos descritos en su [`README.md`](./weather-pipeline/README.md) para ejecutar el pipeline completo.

## 💡 Siguientes Propuestas

Este proyecto se puede extender o mejorar de varias formas:

- 📈 **Modelo más complejo:** Reemplazar el clasificador base por un modelo más robusto que aproveche más variables y componentes temporales como fechas o estacionalidades.
- 🔁 **Entrenamiento incremental:** Implementar lógica que permita reentrenar el modelo solo con los nuevos datos, reduciendo tiempos y recursos.
- 🎨 **Mejora del frontend:** Hacer la app web más interactiva, con visualizaciones adicionales o configuración personalizada de predicciones.
- ☁️ **Despliegue en la nube:** Adaptar el sistema para funcionar en plataformas como GCP, AWS o Azure.
