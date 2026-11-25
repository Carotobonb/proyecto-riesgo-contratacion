"""Agente para la señal 2: lee el objeto del contrato y dice si es claro.

Usa un modelo de lenguaje local con Ollama. Nota: 0 claro, 50 parcial, 100 poco claro.

Uso:
    uv run python -m src.signals.agente data/snapshots/contratos_medellin.csv \
        data/processed/agente.csv --limite 20
"""
import argparse
import json
import os
import time
from pathlib import Path

import ollama
import pandas as pd

MODELO = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

PROMPT = """Eres un auditor de contratación pública en Colombia.
Lee el objeto de un contrato y responde tres preguntas con true o false:

- "que": ¿nombra un bien, una obra, un servicio o un rol concreto?
  Frases generales como "apoyo a la gestión" o "servicios profesionales" solas no cuentan.
- "entrega": ¿dice qué se recibe al final? En una compra es el bien o la licencia;
  en un servicio, la actividad concreta que se hace.
- "para_quien": ¿dice para qué entidad, programa, población o lugar?

Ejemplos:
Objeto: Compra de 50 computadores portátiles para las sedes de la Secretaría de Educación
{{"que": true, "entrega": true, "para_quien": true, "razon": "dice qué bien, cuántos y para quién"}}
Objeto: Prestar servicios de apoyo a la gestión en los procesos de la entidad
{{"que": false, "entrega": false, "para_quien": false, "razon": "no dice qué servicio ni qué entrega"}}

En la razón di qué falta o qué lo hace claro, sin repetir el objeto.
Responde SOLO con el JSON.

Objeto: {objeto}"""

CRITERIOS = ["que", "entrega", "para_quien"]


def es_si(valor) -> bool:
    """El modelo a veces responde "false" como texto en vez de false."""
    if isinstance(valor, str):
        return valor.strip().lower() in ("true", "sí", "si")
    return valor is True


def a_nota(datos: dict) -> dict:
    """Las tres respuestas del modelo se vuelven nota: cumple 3 = 0, cumple 2 = 50, menos = 100.

    El modelo solo responde qué tiene el objeto; la nota la pone esta regla del equipo.
    """
    cumple = {c: es_si(datos.get(c)) for c in CRITERIOS}
    nota = {3: 0, 2: 50}.get(sum(cumple.values()), 100)
    return {"objeto_poco_claro": nota, **cumple, "razon": str(datos.get("razon", "")).strip()}


def evaluar_objeto(objeto: str, modelo: str = MODELO) -> dict:
    """Le pregunta al modelo si el objeto es claro y devuelve la nota."""
    if not isinstance(objeto, str) or not objeto.strip():
        return {"objeto_poco_claro": 100, **dict.fromkeys(CRITERIOS, False), "razon": "objeto vacío"}
    respuesta = ollama.chat(
        model=modelo,
        messages=[{"role": "user", "content": PROMPT.format(objeto=objeto.strip())}],
        format="json",                          # obliga al modelo a responder JSON válido
        options={"temperature": 0},             # misma pregunta, misma respuesta
    )
    return a_nota(json.loads(respuesta["message"]["content"]))


def procesar(entrada: str, salida: str, limite: int | None = None) -> pd.DataFrame:
    """Evalúa los objetos del CSV y guarda cada resultado apenas sale.

    Si el proceso se cae, al correrlo de nuevo sigue con los que faltan.
    """
    df = pd.read_csv(entrada, usecols=["id_contrato", "objeto_del_contrato"])
    if limite:
        df = df.head(limite)
    ruta = Path(salida)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    hechos = set(pd.read_csv(ruta)["id_contrato"]) if ruta.exists() else set()
    pendientes = df[~df["id_contrato"].isin(hechos)]
    print(f"Modelo {MODELO}: {len(hechos)} ya evaluados, faltan {len(pendientes)}")

    for i, fila in enumerate(pendientes.itertuples(index=False), start=1):
        inicio = time.perf_counter()
        try:
            resultado = evaluar_objeto(fila.objeto_del_contrato)
        # si uno falla, se avisa y se sigue; al correr de nuevo se reintenta
        except (ollama.ResponseError, json.JSONDecodeError, ConnectionError) as error:
            print(f"  {i}/{len(pendientes)} {fila.id_contrato}: error ({error})")
            continue
        segundos = round(time.perf_counter() - inicio, 1)
        registro = {"id_contrato": fila.id_contrato, **resultado, "segundos": segundos}
        pd.DataFrame([registro]).to_csv(ruta, mode="a", header=not ruta.exists(), index=False)
        print(f"  {i}/{len(pendientes)} {fila.id_contrato}: "
              f"{resultado['objeto_poco_claro']} ({segundos} s)")

    return pd.read_csv(ruta)


def main() -> None:
    ap = argparse.ArgumentParser(description="Agente de la señal objeto poco claro")
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--limite", type=int, help="evaluar solo los primeros N contratos")
    a = ap.parse_args()

    res = procesar(a.entrada, a.salida, a.limite)
    promedio = res["segundos"].mean()
    print(f"\nListo: {len(res)} contratos en {a.salida}")
    notas = res["objeto_poco_claro"].value_counts().reindex([0, 50, 100], fill_value=0)
    print(f"Claros (0): {notas[0]}  Parciales (50): {notas[50]}  Poco claros (100): {notas[100]}")
    print(f"Tiempo promedio: {promedio:.1f} s por contrato "
          f"(los 2.000 tomarían unas {promedio * 2000 / 3600:.1f} horas)")


if __name__ == "__main__":
    main()