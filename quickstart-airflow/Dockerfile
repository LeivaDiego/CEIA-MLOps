# Este Dockerfile es para crear una imagen de Airflow con un archivo requirements.txt
# que contiene las dependencias necesarias para el proyecto.
FROM apache/airflow:2.10.5-python3.8

# Copiar el archivo requirements.txt al contenedor
COPY requirements.txt /

# Instalar las dependencias de Airflow y las adicionales desde requirements.txt
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
