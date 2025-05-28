# MLOPS con

![Apache Airflow](https://upload.wikimedia.org/wikipedia/commons/d/de/AirflowLogo.png)

## 📝 Descripción

Este repositorio contiene el progreso y la documentación de mi aprendizaje sobre Apache Airflow durante mis prácticas. El objetivo es crear una guía práctica y útil para nuevos miembros del equipo, proporcionando recursos y ejemplos diseñados específicamente para principiantes que desean experimentar con Apache Airflow en un entorno controlado.

## 📑 Tabla de Contenidos

- [📝 Descripción](#-descripción)
- [🛠️ Pre-requisitos](#️-pre-requisitos)
- [📂 Estructura del Repositorio](#-estructura-del-repositorio)
- [⚡ Guía Rápida (Quickstart)](#-guía-rápida-quickstart)
- [📚 Introducción a MLOps](#-introducción-a-mlops)
- [🔍 Próximos Pasos](#-próximos-pasos)

## 🛠️ Pre-requisitos

- 🐳 Tener Docker y Docker Compose instalados en tu PC. Puedes descargar Docker Desktop (que ya incluye Docker Compose) desde [Docker Desktop](https://www.docker.com/products/docker-desktop) y seguir las instrucciones de instalación según tu sistema operativo.

## 📂 Estructura del Repositorio

```text
workspace/
├─ quickstart-airflow/        # Carpeta para el entorno rápido con Apache Airflow
│   ├─ dags/                  # Ejemplos de DAGs para aprender las Bases de Airflow
│   ├─ screenshots/           # Capturas de Pantalla de la interfaz de Airflow
│   ├─ docker-compose.yaml    # Archivo de configuración de contenedores y volumenes de Docker
│   ├─ Dockerfile             # Archivo de configuración de imágen de Docker
│   └─ README.md              # Instrucciones detalladas del quickstart
|
├─ intro-mlops/               # Carpeta con la introducción teórica a MLOps
│   ├─ README.md              # Conceptos teóricos, arquitecturas y herramientas de MLOps
│
└─ README.md                  # Información general del proyecto
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

## 🔍 Próximos Pasos

- Diseñar Arquitectura MLOPs para proyecto
- Definir Componentes y flujo de trabajo
