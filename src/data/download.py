"""Descarga una muestra reproducible de SECOP II desde la API de datos.gov.co.

Pide solo las columnas necesarias (sin cédulas, nombres de personas ni cuentas bancarias),
excluye contratos sin fecha de firma y toma una muestra aleatoria con semilla fija.

Uso:
    uv run python -m src.data.download --desde 2025-01-01 --hasta 2025-12-31 --n 2000
"""
import argparse
import os

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


def _where(desde: str, hasta: str) -> str:
    return (
        "upper(ciudad) like '%MEDELLIN%' "
        "AND fecha_de_firma IS NOT NULL "
        f"AND fecha_de_firma >= '{desde}T00:00:00' "
        f"AND fecha_de_firma <= '{hasta}T23:59:59'"
    )


def descargar(desde: str, hasta: str, n: int = 2000, pagina: int = 5000,
              max_filas: int = 60000, semilla: int = 42) -> pd.DataFrame:
    """Baja todos los contratos de la ventana (por páginas) y devuelve n al azar."""
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
    if len(df) > n:
        df = df.sample(n=n, random_state=semilla).reset_index(drop=True)
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--desde", default="2025-01-01")
    ap.add_argument("--hasta", default="2025-12-31")
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--salida", default="data/raw/contratos_medellin.csv")
    a = ap.parse_args()
    df = descargar(a.desde, a.hasta, a.n)
    df.to_csv(a.salida, index=False)
    print(f"{len(df)} contratos guardados en {a.salida}")


if __name__ == "__main__":
    main()
