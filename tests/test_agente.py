from unittest.mock import patch

from src.signals.agente import a_nota, evaluar_objeto


def test_tres_si_es_claro():
    assert a_nota({"que": True, "entrega": True, "para_quien": True})["objeto_poco_claro"] == 0


def test_dos_si_es_parcial():
    assert a_nota({"que": True, "entrega": False, "para_quien": True})["objeto_poco_claro"] == 50


def test_uno_o_ninguno_es_poco_claro():
    assert a_nota({"que": True})["objeto_poco_claro"] == 100
    assert a_nota({})["objeto_poco_claro"] == 100


def test_entiende_true_y_false_como_texto():
    datos = {"que": "true", "entrega": "false", "para_quien": "true"}
    assert a_nota(datos)["objeto_poco_claro"] == 50


def test_objeto_vacio_no_llama_al_modelo():
    with patch("ollama.chat") as chat:
        assert evaluar_objeto("  ")["objeto_poco_claro"] == 100
        chat.assert_not_called()


def test_lee_la_respuesta_del_modelo():
    respuesta = {"message": {"content": '{"que": true, "entrega": true, "para_quien": true,'
                                        ' "razon": "dice qué, cuánto y para quién"}'}}
    with patch("ollama.chat", return_value=respuesta):
        r = evaluar_objeto("Compra de 50 computadores para la Secretaría de Educación")
    assert r["objeto_poco_claro"] == 0
    assert r["razon"] == "dice qué, cuánto y para quién"