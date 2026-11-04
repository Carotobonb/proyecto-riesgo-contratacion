"""Hoja de revisión manual a ciegas: 20 contratos de puntaje alto y 10 de alerta baja.

Genera dos archivos:
- hoja: los 30 contratos mezclados, SIN puntaje, alerta ni señales, para que quien revisa
  no sepa cuáles marcó el sistema.
- clave: id_contrato con grupo, puntaje y alerta, para comparar después de revisar.

Uso:
    uv run python -m src.review_sheet data/processed/ranking.csv data/review
"""
import argparse
from pathlib import Path

import pandas as pd

COLUMNAS_HOJA = ["id_contrato", "nombre_entidad", "modalidad_de_contratacion",
                 "tipo_de_contrato", "objeto_del_contrato", "valor_del_contrato",
                 "dias_adicionados", "urlproceso"]
PREGUNTAS = ["modalidad_y_justificacion", "objeto_claro", "valor_razonable", "adiciones",
             "proceso_se_abre", "conclusion_persona_1", "conclusion_persona_2",
             "observaciones"]


def armar(ranking: pd.DataFrame, n_altos: int = 20, n_bajos: int = 10,
          semilla: int = 42) -> tuple[pd.DataFrame, pd.DataFrame]:
    """ranking debe venir ordenado (salida de build_ranking)."""
    altos = ranking.head(n_altos).assign(grupo="alto")
    bajos = (ranking[ranking["alerta"] == "baja"]
             .sample(n=n_bajos, random_state=semilla).assign(grupo="bajo"))
    sel = pd.concat([altos, bajos]).sample(frac=1, random_state=semilla).reset_index(drop=True)
    hoja = sel[COLUMNAS_HOJA].copy()
    for c in PREGUNTAS:
        hoja[c] = ""
    clave = sel[["id_contrato", "grupo", "puntaje", "alerta"]].copy()
    return hoja, clave


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ranking")
    ap.add_argument("carpeta")
    a = ap.parse_args()
    hoja, clave = armar(pd.read_csv(a.ranking))
    out = Path(a.carpeta)
    out.mkdir(parents=True, exist_ok=True)
    hoja.to_csv(out / "hoja_revision.csv", index=False, encoding="utf-8-sig")
    clave.to_csv(out / "clave_revision.csv", index=False, encoding="utf-8-sig")
    print(f"Hoja ({len(hoja)} contratos) y clave guardadas en {out}")


if __name__ == "__main__":
    main()
