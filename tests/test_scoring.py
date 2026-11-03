import pandas as pd

from src.scoring.score import alert, rank, score


def _df(rows):
    cols = ["directa", "objeto_poco_claro", "valor_atipico", "adiciones", "sin_enlace",
            "valor_del_contrato"]
    return pd.DataFrame(rows, columns=cols)


def test_score_is_mean_of_five_signals():
    df = _df([[100, 100, 50, 100, 0, 1], [100, 0, 0, 50, 0, 1]])
    assert list(score(df)) == [70, 30]


def test_tie_is_broken_by_contract_value():
    df = _df([[100, 0, 0, 0, 0, 5_000_000], [100, 0, 0, 0, 0, 90_000_000]])
    out = rank(df)
    assert list(out["valor_del_contrato"]) == [90_000_000, 5_000_000]


def test_ties_are_not_split_across_alerts():
    p = pd.Series([80, 80, 80, 20, 20, 20, 0, 0, 0, 0])
    a = alert(p)
    assert set(a[:3]) == {"alta"}


def test_all_zero_scores_are_low():
    assert set(alert(pd.Series([0, 0, 0, 0]))) == {"baja"}
