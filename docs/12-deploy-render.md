# 14 - Despliegue en Render.com (Docker)

Este documento explica cómo desplegar la aplicación FastAPI en Render.com usando Docker.

## Requisitos
- Cuenta en Render.com.
- Repositorio accesible (GitHub/GitLab) con el proyecto.
- Archivo `Dockerfile` en la raíz del proyecto.
- (Opcional) Archivo `render.yaml` para blueprint.

## Dockerfile

El proyecto incluye un `Dockerfile` preparado:

```dockerfile
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8000
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY docs ./docs
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
```

Notas:
- La app escucha en `0.0.0.0` y usa el puerto `PORT` que Render inyecta.
- Se instala `requirements.txt` y se copia el código bajo `/app`.
- Se evita incluir `.env` y `project.db` en la imagen con `.dockerignore`.

## .dockerignore

Se incluye `.dockerignore` para evitar copiar cachés y secretos a la imagen:

```text
.venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.env
project.db
.git/
*.log
README.md
scripts/__pycache__/
```

## Crear servicio en Render (UI)

1. En Render, elige “New +” → “Web Service”.
2. Conecta tu repo y selecciona la rama.
3. Render detectará el `Dockerfile`. Configura:
   - Environment: `Docker`.
   - Health Check Path: `/health`.
   - Region y plan (por ejemplo, `Free`).
4. Variables de entorno:
   - `PORT=8000` (Render lo establece automáticamente; definirlo explícitamente es opcional).
   - `PYTHONUNBUFFERED=1`, `PYTHONDONTWRITEBYTECODE=1` (opcional).
   - `DATABASE_URL` según tu base de datos (ver sección siguiente).
5. Crea el servicio. Render construirá la imagen y arrancará el contenedor.

## Base de datos

- Por defecto, el proyecto usa SQLite (`sqlite:///./project.db`). En Render, el sistema de archivos es efímero, por lo que los datos no son persistentes.
- Para persistencia, configura `DATABASE_URL` a PostgreSQL gestionado por Render o a un servicio externo.
  - Ejemplo: `postgresql://USER:PASSWORD@HOST:PORT/DBNAME`.
  - Asegúrate de que `app/core/config.py` lea `DATABASE_URL` desde el entorno (Pydantic BaseSettings lo soporta).

## Blueprint (opcional)

El archivo `render.yaml` permite despliegue declarativo:

```yaml
services:
  - type: web
    name: fastapi-db-app
    env: docker
    plan: free
    dockerfilePath: ./Dockerfile
    autoDeploy: true
    healthCheckPath: /health
    envVars:
      - key: PORT
        value: "8000"
      - key: PYTHONDONTWRITEBYTECODE
        value: "1"
      - key: PYTHONUNBUFFERED
        value: "1"
      # Configura tu base de datos si corresponde
      # - key: DATABASE_URL
      #   value: "postgresql://USER:PASSWORD@HOST:PORT/DBNAME"
```

Para usarlo: “Blueprints” → “New Blueprint Instance” → selecciona tu repo y rama.

## Pruebas y verificación

- Una vez desplegado, abre la URL pública y verifica:
  - `GET /health` devuelve estado.
  - `GET /` responde `{"Hello":"World"}`.
  - Documentación en `/scalar` si está habilitada.
- Puedes reutilizar `scripts/test_api.ps1` apuntando a la URL pública:
  - `pwsh -File scripts/test_api.ps1 -BaseUrl "https://tu-servicio.onrender.com"`

## Problemas comunes

- Tiempo de build alto: verifica el tamaño del contexto de Docker y `.dockerignore`.
- Error al conectar a DB: revisa `DATABASE_URL` y reglas de firewall/whitelist.
- Puerto incorrecto: asegurarse de usar `--port $PORT` y `0.0.0.0`.