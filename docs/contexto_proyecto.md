# Contexto del proyecto

Resumen para quien se une al proyecto (o para dárselo a un asistente de IA antes de pedirle ayuda). Explica qué estamos haciendo, qué decisiones tomamos y qué falta.

## El curso

- Proyecto II, Especialización en Ciencia de Datos e IA, Universidad de Medellín. Profesor: Juan Camilo Tejada.
- Equipo de 3 personas.
- Entregas: 11 de noviembre, avances (30 %). 25 de noviembre, presentación final de 10 minutos + 5 de preguntas (40 %). Si no nos toca en vivo, se entrega un video con los documentos en enlaces públicos.
- Rúbrica final: descripción del problema 20 %, importancia 10 %, claridad del flujo 10 %, diferenciación 5 %, tecnología adecuada 10 %, viabilidad técnica 15 %, generación de valor 25 %, escalabilidad 5 %.

## La idea

Hay demasiados contratos públicos para revisarlos todos a mano. Queremos ordenarlos para saber cuáles revisar primero.

El profesor sugirió etiquetar los contratos por sus características (cómo se hizo el contrato) y no por quién es el contratista, y usar un agente (modelo de lenguaje) para la parte de texto. El sistema no dice que un contrato sea corrupto: dice cuál conviene mirar primero.

## Datos

- Fuente: SECOP II - Contratos Electrónicos en datos.gov.co (conjunto `jbjy-vk9h`), por la API. Código: `src/data/download.py`.
- Filtro: ciudad Medellín (se busca `MEDELL` sin tilde porque la ciudad viene como "Medellín"), contratos con fecha de firma, ventana móvil de los últimos 24 meses hasta el día en que se corre.
- Muestra: 2.000 contratos al azar, en bloques de 5 contratos seguidos, semilla 42.
- Foto que usamos todos: `data/snapshots/contratos_medellin.csv` con su `.meta.json` (ventana 2024-11-03 a 2026-11-03, 98.763 contratos en la ventana). El sha256 del meta sirve para comprobar que es el mismo archivo.
- Solo pedimos columnas sin datos personales (sin cédulas, nombres de contratistas ni cuentas). El nombre o documento del proveedor no entra al modelo.

## Las 5 señales

Cada señal da 0, 50 o 100. Fuentes y páginas en `docs/senales.md`. Los umbrales son nuestros porque las guías no los fijan para Colombia.

1. Contratación directa: directa 100; directa con ofertas, régimen especial o no definido 50; procesos abiertos 0.
2. Objeto poco claro: hoy es una regla (menos de 8 palabras = 100). La va a reemplazar el agente.
3. Valor atípico: percentil del valor dentro de su tipo de contrato; desde 99 = 100, desde 95 = 50; tipos con menos de 30 contratos no se comparan.
4. Adiciones: días adicionados frente a la duración; menos de 30 % = 50, 30 % o más = 100.
5. Sin enlace al proceso: si no hay `urlproceso`, 100.

Puntaje: promedio de las 5 (0 a 100). Ranking: por puntaje y, si empatan, por valor del contrato. Alertas por posición: primer 10 % alta, siguiente 20 % media, resto baja; puntaje 0 siempre baja.

## Lo que encontramos en la foto

- 87 % contratación directa, casi toda por "servicios profesionales y apoyo a la gestión".
- 20,2 % de los contratos tiene días adicionados.
- El ITM firmó el 38 % de los contratos de la muestra (lo confirmamos con dos formas de muestreo).
- La señal de directa marca casi todo y la de sin enlace no marca nada: hay que ajustarlas. La regla de objeto poco claro casi no marca (por eso el agente).
- Calidad de datos: la misma entidad aparece con nombres distintos (por ejemplo, Pascual Bravo).

## Cómo está organizado el repositorio

- `src/data/download.py`: descarga por la API. `src/data/load.py`: carga y valida.
- `src/signals/compute.py`: las 5 señales. `src/scoring/score.py`: puntaje y alertas.
- `src/build_ranking.py`: arma el ranking. `src/review_sheet.py`: hoja de revisión.
- `notebooks/01_recorrido.ipynb`: todo paso a paso.
- `tests/`: pruebas (`uv run pytest`). GitHub corre ruff y pytest en cada cambio.

Comandos:

```bash
uv sync
uv run pytest
uv run python -m src.data.download
uv run python -m src.build_ranking data/snapshots/contratos_medellin.csv data/processed/ranking.csv
uv run python -m src.review_sheet data/processed/ranking.csv data/review
```

## Cómo trabajamos

- Cada tarea en su rama (`feature/...`) y se une a `main` con una solicitud de extracción.
- No se suben `.env`, datos crudos (`data/raw`), `mlruns` ni la clave de la revisión.
- Antes de subir: `uv run ruff check .` y `uv run pytest`.
- Explicaciones y comentarios cortos y en lenguaje sencillo.

## Estado

Hecho: propuesta y fuentes, descarga por API, foto de datos, 5 señales, puntaje, ranking, hoja de revisión a ciegas (30 contratos: 20 de puntaje alto y 10 de alerta baja), notebook.

Falta, en orden:

1. Agente para la señal 2 (ver abajo).
2. Revisión manual de los 30 contratos, dos personas por separado. La clave (cuáles son altos y bajos) no se mira hasta terminar.
3. Presentación de avances (11 de noviembre).
4. Resultados de la revisión: acuerdo entre las dos personas y cuántos de los 20 altos se confirman.
5. Ajustar las señales de directa y sin enlace.
6. Tablero con el ranking y presentación final.
7. Si hay tiempo: MLflow o Prefect.

## Tarea: agente para "objeto poco claro"

- Rama: `feature/agente`. Archivo: `src/signals/agente.py`.
- Modelo local con Ollama (por ejemplo `qwen2.5:3b`), gratis. Si el computador es lento, Google Colab.
- Entrada: `objeto_del_contrato` de la foto. Pregunta al modelo: si la descripción deja claro qué se compra (qué, cuánto, dónde o para quién). Respuesta en JSON, por ejemplo `{"claro": true, "razon": "..."}`.
- Salida: CSV con `id_contrato`, `objeto_poco_claro` (100 si no es claro, 0 si es claro) y `razon`, guardado a medida que avanza para no repetir si se cae.
- Probar primero con 20 contratos y medir cuánto tarda.
- Conexión con el ranking: `add_signals` ya respeta la columna `objeto_poco_claro` si viene en la tabla. Falta que `build_ranking` reciba el CSV del agente (por ejemplo `--agente ruta.csv`) y lo una por `id_contrato`. Agregar una prueba para eso.
- Para evaluar: comparar lo que dice el agente con lo que digan las personas en la revisión manual de los 30 contratos.

## Fuentes de las señales

- Open Contracting Partnership, Red flags for integrity (2016): https://www.open-contracting.org/wp-content/uploads/2016/11/Red-flags-for-integrity-Giving-the-green-light-to-open-data-solutions-shared.pdf
- IMCO, Compras públicas estatales (2022): https://imco.org.mx/wp-content/uploads/2022/08/Compras-publicas-estatales_IMCO.pdf
- RAI SEE, Training manual on analyzing public procurement risks: https://rai-see.org/php_sets/uploads/2022/02/R2G4P_Training-manual-on-analyzing-public-procurement-risks-2.pdf
- OCDE, DAF/COMP/WD(2025)8/FINAL: https://one.oecd.org/document/DAF/COMP/WD(2025)8/FINAL/en/pdf
- Gallego, Rivero y Martínez, documento de trabajo: https://repository.urosario.edu.co/bitstream/handle/10336/18525/dt222.pdf
