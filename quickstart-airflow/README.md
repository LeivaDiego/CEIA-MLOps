# ⚡ Airflow Quickstart - Versión 2.10.5

## 📝 Descripción

Este entorno de `quickstart-airflow` está diseñado para facilitar la instalación y configuración rápida de Apache Airflow en Windows utilizando Docker. Está basado en la versión **2.10.5** de Apache Airflow y permite experimentar con DAGs personalizados o con los ejemplos predeterminados de Airflow.

> [!IMPORTANT]
> Este entorno es únicamente para fines de experimentación y aprendizaje. No debe ser utilizado en entornos de producción.

## 📑 Tabla de Contenidos

- [📝 Descripción](#-descripción)
- [🛠️ Requisitos Previos](#️-requisitos-previos)
- [📂 Estructura de Carpetas](#-estructura-de-carpetas)
- [🚦 Configuración Inicial](#-configuración-inicial)
- [▶️ Iniciar el Entorno de Apache Airflow](#️-iniciar-el-entorno-de-apache-airflow)
- [📋 Mensajes de Éxito Esperados](#-mensajes-de-éxito-esperados)
- [✅ Verificar el Estado de los Servicios](#-verificar-el-estado-de-los-servicios)
- [🌐 Acceder a la Interfaz Web](#-acceder-a-la-interfaz-web)
- [🧱 Extender la Imagen de Apache Airflow](#-extender-la-imagen-de-apache-airflow)
  - [📦 Paso 1: Crear requirements.txt](#-paso-1-crear-requirementstxt)
  - [🐳 Paso 2: Crear el Dockerfile](#-paso-2-crear-el-dockerfile)
  - [📄 Paso 3: Modificar docker-compose.yaml](#-paso-3-modificar-docker-composeyaml)
  - [🧪 Paso 4: Reconstruir la Imagen](#-paso-4-reconstruir-la-imagen)
- [🛑 Detener el Entorno](#-detener-el-entorno)
- [🧹 Eliminar Contenedores y Volúmenes](#-eliminar-contenedores-y-volúmenes)
- [💻 Uso de VSCode con Dev Containers](#-uso-de-vscode-con-dev-containers)
  - [🔧 Pre-requisitos](#-pre-requisitos)
  - [⚙️ Pasos para Configurar el Dev Container](#️-pasos-para-configurar-el-dev-container)

## 🛠️ Requisitos Previos

- Tener **Docker** y **Docker Compose** instalados en tu PC. (Docker Desktop ya incluye Docker Compose).

Si aun no lo tienes dirigete a [Docker Desktop](https://www.docker.com/products/docker-desktop) y sigue las instrucciones de instalación según tu sistema operativo.

## 📂 Estructura de Carpetas

```text
quickstart-airflow/
├─ dags/                        # Ejemplos de DAGs
│   ├─ dag_hello_world.py         # Ejemplo inicial de un DAG
│   ├─ dag_bash_operator.py       # Ejemplo de un DAG con BashOperator
│   ├─ dag_dependencies.py        # Ejemplo de un DAG con dependencias entre tareas
│   ├─ dag_branching.py           # Ejemplo de un DAG con ramas
│   ├─ dag_weatherapi.py          # Ejemplo de un DAG que utiliza un servicio externo
│   └─ README.md                  # Guía de uso y explicación de los DAGs
|
├─ plugins/               # Plugins personalizados (si son necesarios)
├─ config/                # Archivos de configuración (en gitignore)
├─ logs/                  # Carpeta de logs (en gitignore)
├─ docker-compose.yaml    # Archivo de configuración Docker
├─ Dockerfile             # Archivo básico de docker para airflow
├─ .env                   # Variables de entorno necesarias
└─ README.md              # Instrucciones detalladas del quickstart
```

> [!NOTE]
> Las carpetas `plugins`, `config`, `logs` y el archivo `.env` no están presentes en el repositorio debido a que:
>
> - `plugins/`, `config/`, y `logs/` deben ser generados localmente antes de iniciar el entorno.
> - `.env` contiene información de configuración específica del entorno local.  
> Estos elementos están incluidos en el `.gitignore` para evitar problemas de seguridad y asegurar una configuración adecuada en cada entorno.

## 🚦 Configuración Inicial

1. Navega a la carpeta `quickstart-airflow`:

   ```bash
   cd workspace/quickstart-airflow
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

## ▶️ Iniciar el Entorno de Apache Airflow

1. Antes de comenzar asegurate de haber ejecutado docker desktop para que este activo el Daemon.

2. Ejecuta el siguiente comando para inicializar Apache Airflow:

   ```bash
   # Inicializar la base de datos y servicios
   docker compose up airflow-init
   ```

   > [!IMPORTANT]
   > Solo es necesario ejecutar el comando anterior la primera vez que inicializas el entorno.

3. Ejecuta el siguiente comando para ejecutar Apache Airflow :

   ```bash
   # Iniciar todos los servicios en segundo plano
   docker compose up -d
   ```

   >[!TIP]
   > Utilice la bandera `-d` o `--detach` para ejecutar el compose de Apache Airflow en segundo plano y tener una terminal mas limpia.

## 📋 Mensajes de Éxito Esperados

Durante la inicialización, deberías ver mensajes como:

- `airflow-init-1  | User "airflow" created with role "Admin"` (Indica que el se ha creado el usuario predeterminado correctamente)
- `airflow-init-1  | 2.10.5` (Indica la versión utilizada de Apache Airflow)
- `airflow-init-1 exited with code 0` (La inicialización ha sido exitosa)

Si todo está en orden, podrás acceder a la interfaz web y ver los DAGs cargados.

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

Asegúrate de que todos los servicios estén en estado **healthy**. Si dicen `health: starting`, espera un momento y vuelve a intentar abrir la interfaz.

## 🌐 Acceder a la Interfaz Web

1. Abre tu navegador y dirígete a:

   [http://localhost:8080](http://localhost:8080)

2. Inicia sesión con las credenciales predeterminadas:

   - **Usuario:** airflow
   - **Contraseña:** airflow

3. Deberías de ver algo como esto:

   ![Airflow GUI](screenshots/airflow-gui.png)

## 🧱 Extender la Imagen de Apache Airflow

Por defecto, este entorno usa la imagen oficial de Apache Airflow (apache/airflow:2.10.5). Sin embargo, cuando queremos **agregar paquetes adicionales** (por ejemplo, para consumir APIs externas o procesar archivos), es una mejor práctica extender la imagen base mediante un `Dockerfile` y un archivo `requirements.txt`.

> [!IMPORTANT]
> Apache recomienda no usar `_PIP_ADDITIONAL_REQUIREMENTS` para el desarrollo local, porque esto provoca que los contenedores tarden más en iniciar y causar conflictos. Lo mejor es crear una imagen personalizada.

### 📦 Paso 1: Crear requirements.txt

En la raíz del proyecto, crea un archivo llamado requirements.txt con el siguiente contenido:

```bash
requests
```

Puedes agregar cualquier otro paquete de PyPI necesario para tus DAGs. En este caso solo necesitamos el paquete de `requests` ya que usaremos [Weather API](https://www.weatherapi.com/)

### 🐳 Paso 2: Crear el Dockerfile

También en la capreta `quickstart-airflow` (junto a tu `docker-compose.yaml`), crea un archivo llamado `Dockerfile` con el siguiente contenido:

```dockerfile
FROM apache/airflow:2.10.5

# Copiamos el archivo con dependencias
COPY requirements.txt .

# Instalamos Airflow en la misma versión para evitar conflictos, más nuestras dependencias
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r requirements.txt
```

### 📄 Paso 3: Modificar docker-compose.yaml

Ubica esta sección en la parte superior del archivo:

```yaml
x-airflow-common:
  &airflow-common
  image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.5}
  # build: .
```

Y comenta la linea con image y descomenta la de build asi:

```yaml
x-airflow-common:
  &airflow-common
  # image: ${AIRFLOW_IMAGE_NAME:-apache/airflow:2.10.5}
  build: .
```

> [!TIP]
> Esto le dice a Docker Compose que construya una imagen personalizada usando el Dockerfile y el requirements.txt que creaste.

### 🧪 Paso 4: Reconstruir la Imagen

Cada vez que modifiques el Dockerfile o el requirements.txt, debes reconstruir la imagen con:

```bash
docker compose build
```

Y luego iniciar el entorno como siempre:

```bash
docker compose up -d
```

También puedes usar:

```bash
docker compose up --build -d
```

para forzar la reconstrucción al levantar el entorno.

## 🛑 Detener el Entorno

Para detener la ejecución del entorno utiliza el siguiente comando:

```bash
docker compose down
```

## 🧹 Eliminar Contenedores y Volúmenes

- Si quieres empezar desde 0 otra vez, ejecuta el siguiente comando:

   ```bash
   docker compose down --volumes --remove-orphans
   ```

   > [!CAUTION]
   > Esto eliminará todos los volúmenes y datos almacenados, listo para empezar de nuevo.

- Si ya no necesitas el entorno y deseas limpiar todos los contenedores y volúmenes asociados, ejecuta el siguiente comando:

  ```bash
   docker compose down --volumes --remove-orphans --rmi all
  ```

   >[!CAUTION]
   > Esto eliminará todos los volúmenes, datos almacenados e imágenes descargadas.

## 💻 Uso de VSCode con Dev Containers

> [!TIP]
> Para tener una mejor experiencia desarrollando DAGs, sigue los pasos a continuación para utilizar la extensión de `Dev Containers` de *VSCode* para poder tener acceso a Airflow dentro del entorno de Docker.

### 🔧 Pre-requisitos

1. **Docker Desktop:** Instalar Docker desde [Docker Hub](https://www.docker.com/products/docker-desktop).
2. **Visual Studio Code (VS Code):** Descargar desde [Visual Studio Code](https://code.visualstudio.com/).
3. **Extensión Dev Containers:** Instalar la extensión oficial de Microsoft: `Dev Containers` en VS Code.
   ![alt text](screenshots/dev-containers-ext.png)

4. **Archivo `docker-compose.yaml` oficial de Apache Airflow:** Descargable desde el [repositorio oficial](https://github.com/apache/airflow).

### ⚙️ Pasos para Configurar el Dev Container

1. **Crear un Dockerfile:** En el mismo directorio donde está el `docker-compose.yaml`, crea un archivo `Dockerfile` con el siguiente contenido mínimo:

   > [!NOTE]
   > Esta paso no es necesario si ya has pasado por la seccion [🧱 Extender la Imagen de Apache Airflow](#-extender-la-imagen-de-apache-airflow)

   ```dockerfile
   FROM apache/airflow:<version>
   # Ejemplo: FROM apache/airflow:2.10.5-python3.8
   ```

2. **Agregar Configuración de Dev Container:**

   > [!IMPORTANT]
   > El proceso puede tardar unos minutos en lo que se descargan los elementos necesarios para la conexión remota.

   - Abre VS Code y navega a la paleta de comandos (`Ctrl + Shift + P`).
   - Escribe `Dev Containers: Add Development Container Configuration Files`.
   - Selecciona `Add configuration to workspace` para crear en el directorio de trabajo la carpeta de configuraciones
   - Selecciona `From Dockerfile` y elige elementos adicionales si lo deseas o solo da en `ok`.
  
3. **Reabrir en el Contenedor:**
   - Nuevamente, usa `Ctrl + Shift + P`, escribe `Dev Containers: Reopen in Container` y selecciónalo.
   - VS Code construirá el contenedor y se abrirá en una nueva ventana.

4. **Instalar la Extensión de Python:**
   - Abre el panel de extensiones en VS Code, busca `Python` y selecciona `Install in Dev Container` para habilitar el Intellisense.

5. **Seleccionar el Intérprete de Python:**
   - Haz clic en la barra inferior izquierda (`Select Python Interpreter`) y elige el intérprete del entorno Docker (En este caso python 3.8).

6. **Abrir una Terminal Local:**

   > [!TIP]
   > Este paso es opcional si quieres tener acceso a una terminal de tu máquina local y no del contenedor, pero es muy útil para reiniciar el contenedor del webserver para actualizar la vista de los DAGs en la UI de Airflow.

   - Usa `Ctrl + Shift + P` y selecciona `Create New Integrated Terminal (Local)`.

7. **Cerrar el Dev Container:**
   - Para salir del entorno, usa `Ctrl + Shift + P`, busca `Close Dev Container` y seleccionaló.
