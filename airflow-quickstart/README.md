# ⚡ Airflow Quickstart - Versión 2.10.5

## 🚀 Descripción

Este entorno de `airflow-quickstart` está diseñado para facilitar la instalación y configuración rápida de Apache Airflow en Windows utilizando Docker. Está basado en la versión **2.10.5** de Apache Airflow y permite experimentar con DAGs personalizados o con los ejemplos predeterminados de Airflow.

⚠️ **Nota:** Este entorno es únicamente para fines de experimentación y aprendizaje. No debe ser utilizado en entornos de producción.

---

## 🛠️ Requisitos Previos

- Tener **Docker** y **Docker Compose** instalados en tu PC. (Docker Desktop ya incluye Docker Compose).

---

## 📂 Estructura de Carpetas

```
airflow-quickstart/
├─ dags/                  # Ejemplos de DAGs o DAGs personalizados
├─ plugins/               # Plugins personalizados (si son necesarios)
├─ config/                # Archivos de configuración (en gitignore)
├─ logs/                  # Carpeta de logs (en gitignore)
├─ docker-compose.yaml    # Archivo de configuración Docker
├─ .env                   # Variables de entorno necesarias
└─ README.md              # Instrucciones detalladas del quickstart
```

---

## 🚦 Configuración Inicial

1. Navega a la carpeta `airflow-quickstart`:

```bash
cd workspace/airflow-quickstart
```

2. Crea las carpetas necesarias y el archivo `.env`:

```bash
mkdir dags plugins config logs

# Crear el archivo .env con el ID de usuario para evitar warnings
echo "AIRFLOW_UID=50000" > .env
```

3. Configura la carga de ejemplos de Apache Airflow:

En el archivo `docker-compose.yaml`, puedes habilitar o deshabilitar la carga de DAGs de ejemplo cambiando el valor de la variable `AIRFLOW__CORE__LOAD_EXAMPLES`:

```yaml
AIRFLOW__CORE__LOAD_EXAMPLES: 'true' # Cambia a 'false' para no cargar ejemplos
```

---

## 🚀 Iniciar el Entorno de Apache Airflow

Ejecuta el siguiente comando para inicializar Apache Airflow:
*❕ Solo ejecutar este comando la primera vez*
```bash
# Inicializar la base de datos y servicios
docker compose up airflow-init
```

Ejecuta el siguiente comando para ejecutar Apache Airflow :
```bash
# Iniciar todos los servicios en segundo plano
docker compose up -d
```
*Nota: la bandera `-d` es `--detach` para ejecutarlo en segundo plano y evitar llenar de logs la terminal*
---

## 📋 Mensajes de Éxito Esperados

Durante la inicialización, deberías ver mensajes como:

- `airflow-init-1  | User "airflow" created with role "Admin"` (Indica que el se ha creado el usuario predeterminado correctamente)
- `airflow-init-1  | 2.10.5` (Indica la versión utilizada de Apache Airflow)
- `airflow-init-1 exited with code 0` (La inicialización ha sido exitosa)

Si todo está en orden, podrás acceder a la interfaz web y ver los DAGs cargados.

---

## ✅ Verificar el Estado de los Servicios

Si la interfaz web no se carga, ejecuta el siguiente comando para verificar el estado de los contenedores:

```bash
docker ps
```

y debería de verse algo como esto:
```bash
CONTAINER ID   IMAGE                   COMMAND                  CREATED          STATUS                    PORTS                              NAMES
247ebe6cf87a   apache/airflow:2.10.5   "/usr/bin/dumb-init …"   3 minutes ago    Up 3 minutes (healthy)    8080/tcp                           compose_airflow-worker_1
ed9b09fc84b1   apache/airflow:2.10.5   "/usr/bin/dumb-init …"   3 minutes ago    Up 3 minutes (healthy)    8080/tcp                           compose_airflow-scheduler_1
7cb1fb603a98   apache/airflow:2.10.5   "/usr/bin/dumb-init …"   3 minutes ago    Up 3 minutes (healthy)    0.0.0.0:8080->8080/tcp             compose_airflow-webserver_1
74f3bbe506eb   postgres:13             "docker-entrypoint.s…"   18 minutes ago   Up 17 minutes (healthy)   5432/tcp                           compose_postgres_1
0bd6576d23cb   redis:latest            "docker-entrypoint.s…"   10 hours ago     Up 17 minutes (healthy)   0.0.0.0:6379->6379/tcp             compose_redis_1
```

Asegúrate de que todos los servicios estén en estado **healthy**.

---

## 🌐 Acceder a la Interfaz Web

1. Abre tu navegador y dirígete a:

[http://localhost:8080](http://localhost:8080)

2. Inicia sesión con las credenciales predeterminadas:

- **Usuario:** airflow
- **Contraseña:** airflow

---

## Detener el Entorno

Para detener la ejecución del entorno utiliza el siguiente comando:
```bash
docker compose down
```          

---

## 🧹 Eliminar Contenedores y Volúmenes

- Si quieres empezar desde 0 otra vez, ejecuta el siguiente comando:
```bash
docker compose down --volumes --remove-orphans
```          
⚠️ **Advertencia:** Esto eliminará todos los volúmenes y datos almacenados, listo para empezar de nuevo.


- Si ya no necesitas el entorno y deseas limpiar todos los contenedores y volúmenes asociados, ejecuta el siguiente comando:
```bash
docker compose down --volumes --rmi all
```
⚠️ **Advertencia:** Esto eliminará todos los volúmenes, datos almacenados e imágenes descargadas.
