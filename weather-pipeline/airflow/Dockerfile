# Imagen base de Airflow 2.10.5
FROM apache/airflow:2.10.5

# Instalación de dependencias del sistema operativo
# Copia el archivo de requisitos al contenedor
COPY requirements.txt /requirements.txt
# Instala las dependencias del sistema operativo
RUN pip install --no-cache-dir -r /requirements.txt