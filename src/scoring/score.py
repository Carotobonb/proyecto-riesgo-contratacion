"""Puntaje de riesgo, desempate y alerta."""
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


def alert(puntaje: pd.Series, q_alta: float = 0.90, q_media: float = 0.70) -> pd.Series:
    """Alerta relativa por percentiles. Los empates no se parten: mismo puntaje, misma alerta.

    Un puntaje de 0 nunca queda en alerta alta ni media.
    """
    t_alta = puntaje.quantile(q_alta)
    t_media = puntaje.quantile(q_media)
    out = pd.Series("baja", index=puntaje.index)
    out[(puntaje >= t_media) & (puntaje > 0)] = "media"
    out[(puntaje >= t_alta) & (puntaje > 0)] = "alta"
    return out
