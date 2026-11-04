import pandas as pd

from src.review_sheet import COLUMNAS_HOJA, armar


def _ranking(n=200):
    df = pd.DataFrame({c: [f"{c}{i}" for i in range(n)] for c in COLUMNAS_HOJA})
    df["puntaje"] = sorted(range(n), reverse=True)
    df["alerta"] = ["alta"] * 20 + ["media"] * 40 + ["baja"] * (n - 60)
    return df


def test_hoja_a_ciegas_y_clave():
    r = _ranking()
    hoja, clave = armar(r)
    assert len(hoja) == 30 and len(clave) == 30
    assert not {"puntaje", "alerta", "grupo"} & set(hoja.columns)     # a ciegas
    assert (clave["grupo"] == "alto").sum() == 20
    altos = set(clave.loc[clave.grupo == "alto", "id_contrato"])
    assert altos == set(r.head(20)["id_contrato"])
    assert set(clave.loc[clave.grupo == "bajo", "alerta"]) == {"baja"}
    assert list(hoja["id_contrato"]) == list(clave["id_contrato"])


def test_es_reproducible():
    r = _ranking()
    assert armar(r)[1].equals(armar(r)[1])
