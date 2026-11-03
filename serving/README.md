# Despliegue

- `batch/`: predicción por lotes con un `batch_id` por corrida, guardada con la versión del modelo.
- `api/`: FastAPI con `/health`, `/predict`, `/predict/batch`, validación con Pydantic, `Dockerfile` y `docker-compose.yml`.

Decisión pendiente del equipo: batch, online o ambos (justificar).
