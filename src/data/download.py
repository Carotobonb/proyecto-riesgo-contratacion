"""Descarga una muestra reproducible de SECOP II desde la API de datos.gov.co.

Pide solo las columnas necesarias (sin cédulas, nombres de personas ni cuentas bancarias),
excluye contratos sin fecha de firma y toma una muestra aleatoria con semilla fija.

Por defecto la ventana es móvil: los últimos 24 meses hasta el día en que se ejecuta.
Cada descarga deja un archivo .meta.json con la ventana, la semilla y el checksum del CSV,
para saber exactamente con qué datos se trabajó.

Uso:
    uv run python -m src.data.download                  # últimos 24 meses hasta hoy
    uv run python -m src.data.download --meses 12       # últimos 12 meses
    uv run python -m src.data.download --desde 2025-01-01 --hasta 2025-12-31   # fijas
"""
import argparse
import hashlib
import json
import os
from datetime import date, datetime

import pandas as pd
import requests

URL = "https://www.datos.gov.co/resource/jbjy-vk9h.json"
COLUMNAS = [
    "id_contrato", "proceso_de_compra", "nombre_entidad", "ciudad", "estado_contrato",
    "modalidad_de_contratacion", "justificacion_modalidad_de", "tipo_de_contrato",
    "objeto_del_contrato", "fecha_de_firma", "fecha_de_inicio_del_contrato",
    "fecha_de_fin_del_contrato", "valor_del_contrato", "dias_adicionados",
    "el_contrato_puede_ser_prorrogado", "urlproceso",
]


def ventana(hoy: date, meses: int) -> tuple[str, str]:
    """Devuelve (desde, hasta) en formato AAAA-MM-DD: los últimos `meses` hasta `hoy`."""
    desde = (pd.Timestamp(hoy) - pd.DateOffset(months=meses)).date()
    return desde.isoformat(), hoy.isoformat()


def checksum(ruta: str) -> str:
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for bloque in iter(lambda: f.read(1 << 20), b""):
            h.update(bloque)
    return h.hexdigest()


def _where(desde: str, hasta: str) -> str:
    return (
        "upper(ciudad) like '%MEDELLIN%' "
        "AND fecha_de_firma IS NOT NULL "
        f"AND fecha_de_firma >= '{desde}T00:00:00' "
        f"AND fecha_de_firma <= '{hasta}T23:59:59'"
    )


def descargar(desde: str, hasta: str, n: int = 2000, pagina: int = 5000,
              max_filas: int = 60000, semilla: int = 42) -> tuple[pd.DataFrame, int]:
    """Baja todos los contratos de la ventana (por páginas) y devuelve n al azar.

    También devuelve cuántos contratos había en la ventana antes de muestrear.
    """
    headers = {}
    if os.getenv("SOCRATA_APP_TOKEN"):
        headers["X-App-Token"] = os.environ["SOCRATA_APP_TOKEN"]
    filas, offset = [], 0
    while offset < max_filas:
        params = {
            "$select": ",".join(COLUMNAS),
            "$where": _where(desde, hasta),
            "$order": "id_contrato",
            "$limit": pagina,
            "$offset": offset,
        }
        r = requests.get(URL, params=params, headers=headers, timeout=120)
        r.raise_for_status()
        lote = r.json()
        filas.extend(lote)
        if len(lote) < pagina:
            break
        offset += pagina
    df = pd.DataFrame(filas)
    total = len(df)
    if total > n:
        df = df.sample(n=n, random_state=semilla).reset_index(drop=True)
    return df, total


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--meses", type=int, default=24, help="ventana móvil hasta hoy")
    ap.add_argument("--desde", help="fecha fija de inicio (AAAA-MM-DD)")
    ap.add_argument("--hasta", help="fecha fija de fin (AAAA-MM-DD)")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--semilla", type=int, default=42)
    ap.add_argument("--salida", default="data/raw/contratos_medellin.csv")
    a = ap.parse_args()

    desde, hasta = ventana(date.today(), a.meses)
    desde, hasta = a.desde or desde, a.hasta or hasta

    df, total = descargar(desde, hasta, a.n, semilla=a.semilla)
    df.to_csv(a.salida, index=False)
    meta = {
        "desde": desde,
        "hasta": hasta,
        "contratos_en_ventana": total,
        "muestra": len(df),
        "semilla": a.semilla,
        "sha256": checksum(a.salida),
        "descargado": datetime.now().isoformat(timespec="seconds"),
    }
    with open(a.salida.replace(".csv", ".meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"{len(df)} de {total} contratos ({desde} a {hasta}) guardados en {a.salida}")


if __name__ == "__main__":
    main()
