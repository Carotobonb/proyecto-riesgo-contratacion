# Arquitectura

Datos (API datos.gov.co) -> validación -> señales (reglas + agente) -> puntaje y alerta -> modelo -> registro (candidate/champion) -> batch o API -> monitoreo y tablero.

Cada ejecución debe poder reproducirse: código en Git, entorno en `uv.lock`, datos identificados por checksum, parámetros y métricas en MLflow.
