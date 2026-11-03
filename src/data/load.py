"""Carga y validación del CSV de contratos."""
import pandas as pd

REQUERIDAS = [
    "id_contrato", "nombre_entidad", "modalidad_de_contratacion", "tipo_de_contrato",
    "objeto_del_contrato", "fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato",
    "valor_del_contrato", "dias_adicionados", "urlproceso",
]


def cargar(ruta: str) -> pd.DataFrame:
    df = pd.read_csv(ruta, low_memory=False)
    faltan = [c for c in REQUERIDAS if c not in df.columns]
    if faltan:
        raise ValueError(f"Faltan columnas en {ruta}: {faltan}")
    df = df.drop_duplicates(subset="id_contrato").copy()
    df["valor_del_contrato"] = pd.to_numeric(df["valor_del_contrato"], errors="coerce")
    df["dias_adicionados"] = pd.to_numeric(df["dias_adicionados"], errors="coerce").fillna(0)
    for c in ("fecha_de_inicio_del_contrato", "fecha_de_fin_del_contrato"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df.reset_index(drop=True)
