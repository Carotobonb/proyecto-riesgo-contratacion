# Detección de riesgo en la contratación pública (SECOP II, Medellín)

Proyecto II. Ordena los contratos de SECOP II según señales de riesgo que se leen del contrato, para decidir cuáles revisar primero. El sistema no acusa a nadie: prioriza la revisión.

## Cómo reproducirlo

```bash
git clone <url-del-repositorio>
cd proyecto-riesgo-contratacion
uv sync
cp .env.example .env        # y completar los valores reales
uv run pytest
```

Requiere Python 3.11 o superior y [uv](https://docs.astral.sh/uv/). El archivo `uv.lock` se genera con `uv sync` y se sube al repositorio.

## Estructura

| Carpeta | Qué contiene |
|---|---|
| `data/raw` | Muestra descargada de la API de datos.gov.co. No se versiona. |
| `data/processed` | Tablas con señales y puntaje. No se versiona. |
| `data/snapshots` | Foto de datos fija (CSV + .meta.json) que usa todo el equipo para el análisis. Sí se versiona. |
| `data/review` | Hoja de revisión manual a ciegas (20 altos y 10 bajos) y su clave. |
| `notebooks` | Exploración. El código reutilizable pasa a `src`. |
| `src/data` | Descarga por la API, validación y selección de columnas. |
| `src/signals` | Las 5 señales: reglas sobre campos y agente que lee el objeto del contrato. |
| `src/scoring` | Puntaje de 0 a 100, desempate y alerta baja, media o alta. |
| `src/models` | Entrenamiento, búsqueda de hiperparámetros y registro del modelo. |
| `orchestration` | Flujo de Prefect que une todos los pasos. |
| `serving` | Predicción por lotes y API (FastAPI + Docker). |
| `monitoring` | Señales para vigilar datos y modelo. |
| `dashboard` | Ranking de contratos y señales que marcó cada uno. |
| `tests` | Pruebas automáticas. |
| `docs` | Fuentes de las señales, arquitectura y rúbrica de revisión. |
| `reports` | Presentación y entregables. |

## Flujo de trabajo

```bash
uv run python -m src.data.download                      # API: últimos 24 meses hasta hoy
uv run python -m src.build_ranking data/snapshots/contratos_medellin.csv data/processed/ranking.csv
uv run python -m src.review_sheet data/processed/ranking.csv data/review
```

Para el análisis y la presentación todos usan la foto de `data/snapshots`, así trabajan con
los mismos contratos. Se comprueba con el `sha256` de su `.meta.json`.

## Datos y secretos

- No se suben datos crudos, `.env`, ni `mlruns/`.
- La tabla de SECOP II trae cédulas, nombres y números de cuenta. Se piden solo las columnas necesarias y el proveedor no entra como variable del modelo.
