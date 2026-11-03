"""Arma el ranking de contratos: carga, señales, puntaje, desempate y alerta.

Uso:
    uv run python -m src.build_ranking data/raw/contratos_medellin.csv data/processed/ranking.csv
"""
import argparse

from src.data.load import cargar
from src.scoring.score import SIGNALS, alert, rank
from src.signals.compute import add_signals

SALIDA = ["id_contrato", "nombre_entidad", "modalidad_de_contratacion", "tipo_de_contrato",
          "valor_del_contrato", "puntaje", "alerta", *SIGNALS, "urlproceso"]


def construir(ruta_entrada: str):
    df = add_signals(cargar(ruta_entrada))
    ranking = rank(df)
    ranking["alerta"] = alert(ranking["puntaje"])
    return ranking[SALIDA]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada")
    ap.add_argument("salida")
    a = ap.parse_args()
    construir(a.entrada).to_csv(a.salida, index=False)
    print(f"Ranking guardado en {a.salida}")


if __name__ == "__main__":
    main()
