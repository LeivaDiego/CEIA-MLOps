# /app/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias del sistema (como curl)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar backend y frontend
COPY backend/ /app/backend/
COPY frontend/ /app/frontend/

# Ejecutar FastAPI con Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8001"]
