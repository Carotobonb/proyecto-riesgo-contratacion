import pytest

from src.data.load import cargar


def test_faltan_columnas(tmp_path):
    f = tmp_path / "x.csv"
    f.write_text("id_contrato,nombre_entidad\n1,a\n")
    with pytest.raises(ValueError):
        cargar(str(f))
