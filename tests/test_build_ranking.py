import pandas as pd

from src.build_ranking import unir_agente


def _contratos():
    return pd.DataFrame({
        "id_contrato": ["A", "B"],
        "objeto_del_contrato": ["Compra de 50 computadores para la Secretaría de Educación",
                                "Apoyo"],
    })


def test_usa_la_nota_del_agente(tmp_path):
    ruta = tmp_path / "agente.csv"
    pd.DataFrame({"id_contrato": ["A", "B"], "objeto_poco_claro": [50, 0],
                  "razon": ["falta la entrega", "claro"]}).to_csv(ruta, index=False)
    out = unir_agente(_contratos(), str(ruta))
    assert list(out["objeto_poco_claro"]) == [50, 0]
    assert list(out["razon_agente"]) == ["falta la entrega", "claro"]


def test_si_falta_un_contrato_usa_la_regla_simple(tmp_path):
    ruta = tmp_path / "agente.csv"
    pd.DataFrame({"id_contrato": ["A"], "objeto_poco_claro": [0],
                  "razon": ["claro"]}).to_csv(ruta, index=False)
    out = unir_agente(_contratos(), str(ruta))
    assert list(out["objeto_poco_claro"]) == [0, 100]   # "Apoyo" tiene menos de 8 palabras