"""Arma el ranking de contratos: carga, señales, puntaje, desempate y alerta.

Uso:
    uv run python -m src.build_ranking data/raw/contratos_medellin.csv data/processed/ranking.csv

Con el agente (señal 2 leída por el modelo de lenguaje):
    uv run python -m src.build_ranking data/snapshots/contratos_medellin.csv \
        data/processed/ranking_agente.csv --agente data/processed/agente_2000.csv
"""
import argparse

import pandas as pd

from src.data.load import cargar
from src.scoring.score import SIGNALS, alert, rank
from src.signals.compute import add_signals, baseline_objeto

SALIDA = ["id_contrato", "nombre_entidad", "modalidad_de_contratacion", "tipo_de_contrato",
          "objeto_del_contrato", "valor_del_contrato", "dias_adicionados", "puntaje", "alerta",
          *SIGNALS, "urlproceso"]


def unir_agente(df: pd.DataFrame, ruta_agente: str) -> pd.DataFrame:
    """Pone la nota del agente en la señal 2. Si falta algún contrato, usa la regla simple."""
    ag = (pd.read_csv(ruta_agente, usecols=["id_contrato", "objeto_poco_claro", "razon"])
          .drop_duplicates("id_contrato", keep="last")
          .rename(columns={"razon": "razon_agente"}))
    out = df.merge(ag, on="id_contrato", how="left")
    faltan = out["objeto_poco_claro"].isna()
    out.loc[faltan, "objeto_poco_claro"] = baseline_objeto(out[faltan])
    out["objeto_poco_claro"] = out["objeto_poco_claro"].astype(int)
    if faltan.any():
        print(f"Aviso: {faltan.sum()} contratos sin nota del agente; se usó la regla simple")
    return out


def construir(ruta_entrada: str, ruta_agente: str | None = None):
    df = cargar(ruta_entrada)
    if ruta_agente:
        df = unir_agente(df, ruta_agente)
    ranking = rank(add_signals(df))
    ranking["alerta"] = alert(ranking["puntaje"])
    extra = ["razon_agente"] if "razon_agente" in ranking.columns else []
    return ranking[SALIDA + extra]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    ap.add_argument("--agente", help="CSV con las notas del agente (src.signals.agente)")
    a = ap.parse_args()
    construir(a.entrada, a.agente).to_csv(a.salida, index=False)
    print(f"Ranking guardado en {a.salida}")


if __name__ == "__main__":
    main()