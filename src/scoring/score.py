"""Puntaje de riesgo, desempate y alerta."""
import math

import pandas as pd

SIGNALS = [
    "directa",
    "objeto_poco_claro",
    "valor_atipico",
    "adiciones",
    "sin_enlace",
]


def score(df: pd.DataFrame, signals: list[str] = SIGNALS) -> pd.Series:
    """Promedio de las notas (0 a 100) de las señales."""
    return df[signals].mean(axis=1)


def rank(df: pd.DataFrame, value_col: str = "valor_del_contrato") -> pd.DataFrame:
    """Ordena por puntaje y, a igual puntaje, por valor del contrato (mayor primero)."""
    out = df.copy()
    out["puntaje"] = score(out)
    return out.sort_values(["puntaje", value_col], ascending=[False, False]).reset_index(drop=True)


def alert(puntaje: pd.Series, p_alta: float = 0.10, p_media: float = 0.20) -> pd.Series:
    """Alerta por posición en el ranking: 10 % alta, siguiente 20 % media, el resto baja.

    Recibe el puntaje YA ordenado (salida de rank(), que desempata por valor), con índice
    único. Los cortes se hacen sobre ese orden, así los empates no inflan una alerta cuando
    hay pocos puntajes distintos. Un puntaje de 0 nunca queda en alerta alta ni media.
    """
    n = len(puntaje)
    n_alta = math.ceil(p_alta * n)
    n_media = math.ceil(p_media * n)
    pos = pd.Series(range(n), index=puntaje.index)
    out = pd.Series("baja", index=puntaje.index)
    out[(pos < n_alta + n_media) & (puntaje > 0)] = "media"
    out[(pos < n_alta) & (puntaje > 0)] = "alta"
    return out
