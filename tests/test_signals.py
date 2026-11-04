import pandas as pd

from src.signals.compute import (
    add_signals,
    baseline_objeto,
    nota_adiciones,
    nota_modalidad,
    nota_sin_enlace,
    nota_valor,
)


def test_modalidad():
    assert nota_modalidad("Contratación directa") == 100
    assert nota_modalidad("Contratación Directa (con ofertas)") == 50
    assert nota_modalidad("Contratación régimen especial") == 50
    assert nota_modalidad("Licitación pública") == 0
    assert nota_modalidad("Mínima cuantía") == 0


def test_adiciones():
    df = pd.DataFrame({
        "dias_adicionados": [0, 10, 40, 5],
        "fecha_de_inicio_del_contrato": pd.to_datetime(["2025-01-01"] * 3 + [None]),
        "fecha_de_fin_del_contrato": pd.to_datetime(["2025-04-11"] * 3 + ["2025-04-11"]),
    })
    # duración 100 días: 10 es 10 % (50), 40 es 40 % (100); sin fecha de inicio pero con días: 50
    assert list(nota_adiciones(df)) == [0, 50, 100, 50]


def test_sin_enlace():
    df = pd.DataFrame({"urlproceso": ["https://x", None, "  "]})
    assert list(nota_sin_enlace(df)) == [0, 100, 100]


def test_valor_atipico_por_tipo_y_grupos_pequenos():
    grande = pd.DataFrame({"tipo_de_contrato": "A", "valor_del_contrato": range(1, 101)})
    chico = pd.DataFrame({"tipo_de_contrato": "B", "valor_del_contrato": [1, 10**9]})
    df = pd.concat([grande, chico], ignore_index=True)
    n = nota_valor(df)
    assert n.iloc[99] == 100        # el mayor de su tipo
    assert n.iloc[0] == 0
    assert n.iloc[-1] == 0          # grupo de 2: no se compara


def test_objeto_baseline_y_add_signals_respeta_agente():
    df = pd.DataFrame({
        "modalidad_de_contratacion": ["Contratación directa"],
        "tipo_de_contrato": ["Otro"], "valor_del_contrato": [1.0], "dias_adicionados": [0],
        "fecha_de_inicio_del_contrato": pd.to_datetime(["2025-01-01"]),
        "fecha_de_fin_del_contrato": pd.to_datetime(["2025-02-01"]),
        "urlproceso": ["https://x"], "objeto_del_contrato": ["servicios varios"],
    })
    assert list(baseline_objeto(df)) == [100]
    df["objeto_poco_claro"] = [0]                   # el agente dice que es claro
    assert list(add_signals(df)["objeto_poco_claro"]) == [0]
