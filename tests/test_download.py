from datetime import date

from src.data.download import _where, checksum, elegir_bloques, ventana


def test_ventana_movil_hasta_hoy():
    assert ventana(date(2026, 11, 3), 24) == ("2024-11-03", "2026-11-03")
    assert ventana(date(2026, 3, 31), 1) == ("2026-02-28", "2026-03-31")


def test_where_excluye_sin_firma_y_usa_ventana():
    w = _where("2024-11-03", "2026-11-03")
    assert "fecha_de_firma IS NOT NULL" in w
    assert "'%MEDELL%'" in w            # sin tilde, para no perder "Medellín"
    assert "'2024-11-03T00:00:00'" in w and "'2026-11-03T23:59:59'" in w


def test_checksum_cambia_con_el_contenido(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("x\n1\n")
    c1 = checksum(str(f))
    f.write_text("x\n2\n")
    assert checksum(str(f)) != c1


def test_bloques_cubren_toda_la_ventana_sin_solaparse():
    offs = elegir_bloques(total=150_000, n=2000, tam=20, semilla=42)
    assert len(offs) == 100
    assert len(set(offs)) == 100 and all(o % 20 == 0 for o in offs)
    assert max(offs) + 20 <= 150_000
    assert min(offs) < 30_000 and max(offs) > 120_000      # no se queda en los primeros
    assert offs == elegir_bloques(total=150_000, n=2000, tam=20, semilla=42)
