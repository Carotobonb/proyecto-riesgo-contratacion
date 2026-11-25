"""Compara las respuestas del agente con las de otro evaluador (modelo grande o persona).

Uso:
    uv run python -m src.signals.comparar data/processed/agente_revision.csv \
        data/processed/referencia_modelo_grande.csv
"""
import argparse

import pandas as pd
from sklearn.metrics import cohen_kappa_score

CRITERIOS = ["que", "entrega", "para_quien"]


def a_nota(df: pd.DataFrame) -> pd.Series:
    """Misma regla del agente: 3 sí = 0, 2 sí = 50, menos = 100."""
    return df[CRITERIOS].sum(axis=1).map({3: 0, 2: 50}).fillna(100).astype(int)


def main() -> None:
    ap = argparse.ArgumentParser(description="Agente contra otro evaluador")
    ap.add_argument("agente")
    ap.add_argument("referencia")
    a = ap.parse_args()

    ag = pd.read_csv(a.agente)
    ref = pd.read_csv(a.referencia)
    ref["nota"] = a_nota(ref)
    df = ag.merge(ref, on="id_contrato", suffixes=("_ag", "_ref"))
    df = df.rename(columns={"objeto_poco_claro": "nota_ag", "nota": "nota_ref"})
    n = len(df)
    print(f"Contratos comparados: {n}\n")

    print("Coincidencia por criterio:")
    for c in CRITERIOS:
        iguales = (df[f"{c}_ag"] == df[f"{c}_ref"]).sum()
        print(f"  {c:<11} {iguales}/{n}")

    iguales = (df["nota_ag"] == df["nota_ref"]).sum()
    kappa = cohen_kappa_score(df["nota_ag"], df["nota_ref"])
    print(f"\nMisma nota (0/50/100): {iguales}/{n} ({iguales / n:.0%})")
    print(f"Kappa de Cohen: {kappa:.2f}  (0 = como al azar, 1 = acuerdo perfecto)")

    print("\nNotas (filas: agente, columnas: referencia):")
    print(pd.crosstab(df["nota_ag"], df["nota_ref"], margins=True, margins_name="total"))

    print("\nDonde no coinciden:")
    for f in df[df["nota_ag"] != df["nota_ref"]].itertuples():
        print(f"- {f.id_contrato}: agente {f.nota_ag} / referencia {f.nota_ref}")
        print(f"    agente:     {f.razon_ag}")
        print(f"    referencia: {f.razon_ref}")


if __name__ == "__main__":
    main()