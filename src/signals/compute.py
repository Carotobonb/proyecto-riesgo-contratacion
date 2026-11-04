"""Las cinco señales de riesgo. Cada una devuelve una nota de 0, 50 o 100.

Las reglas y los umbrales son una propuesta del equipo (las fuentes no los fijan para
Colombia) y se ajustan con la revisión manual. Ver docs/senales.md.
"""
import pandas as pd

MIN_GRUPO = 30          # contratos mínimos de un tipo para comparar valores
PCT_ALTO, PCT_MUY_ALTO = 0.95, 0.99
RATIO_ADICION_ALTA = 0.30
PALABRAS_MIN_OBJETO = 8


def nota_modalidad(modalidad: str) -> int:
    """Contratación directa 100; con ofertas o régimen especial 50; procesos abiertos 0."""
    t = str(modalidad).lower()
    if "directa" in t:
        return 50 if "con ofertas" in t else 100
    if "régimen especial" in t or "regimen especial" in t or "no definido" in t:
        return 50
    return 0


def nota_valor(df: pd.DataFrame) -> pd.Series:
    """Percentil del valor dentro de su tipo de contrato. Grupos pequeños no se comparan."""
    pct = df.groupby("tipo_de_contrato")["valor_del_contrato"].rank(pct=True)
    tam = df.groupby("tipo_de_contrato")["valor_del_contrato"].transform("size")
    nota = pd.Series(0, index=df.index)
    nota[pct >= PCT_ALTO] = 50
    nota[pct >= PCT_MUY_ALTO] = 100
    nota[(tam < MIN_GRUPO) | (df["valor_del_contrato"].fillna(0) <= 0)] = 0
    return nota


def nota_adiciones(df: pd.DataFrame) -> pd.Series:
    """0 sin adiciones; 50 si es menos del 30 % de la duración; 100 si es más."""
    dur = (df["fecha_de_fin_del_contrato"] - df["fecha_de_inicio_del_contrato"]).dt.days
    ratio = df["dias_adicionados"] / dur.where(dur > 0)
    nota = pd.Series(0, index=df.index)
    con = df["dias_adicionados"] > 0
    nota[con] = 50
    nota[con & (ratio >= RATIO_ADICION_ALTA)] = 100
    return nota


def nota_sin_enlace(df: pd.DataFrame) -> pd.Series:
    vacio = df["urlproceso"].isna() | (df["urlproceso"].astype(str).str.strip() == "")
    return vacio.map({True: 100, False: 0})


def baseline_objeto(df: pd.DataFrame) -> pd.Series:
    """Referencia simple: objeto con menos de 8 palabras. El agente la reemplaza."""
    palabras = df["objeto_del_contrato"].fillna("").astype(str).str.split().str.len()
    return (palabras < PALABRAS_MIN_OBJETO).map({True: 100, False: 0})


def add_signals(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["directa"] = out["modalidad_de_contratacion"].map(nota_modalidad)
    if "objeto_poco_claro" not in out.columns:      # si ya viene del agente, se respeta
        out["objeto_poco_claro"] = baseline_objeto(out)
    out["valor_atipico"] = nota_valor(out)
    out["adiciones"] = nota_adiciones(out)
    out["sin_enlace"] = nota_sin_enlace(out)
    return out
