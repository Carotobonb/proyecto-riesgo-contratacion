# Orquestación (Prefect)

Un flow que une: descargar muestra, calcular señales, puntuar, entrenar y registrar.
Archivos previstos: `pipeline.py` (flow principal) y `deploy.py` (programación). El flow importa funciones de `src/`; no reescribe la lógica dentro del orquestador.

Reglas de la clase: reintentos solo para fallos transitorios (red, límite de la API), tareas idempotentes, secretos fuera del código.
