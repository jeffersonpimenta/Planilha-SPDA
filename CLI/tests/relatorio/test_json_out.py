import json
from spda.app import analisar
from spda.relatorio.json_out import gerar_json, salvar_json
from spda.model.resultado import Resultado
from tests.test_app import _projeto


def test_gerar_json_roundtrip():
    r = analisar(_projeto())
    txt = gerar_json(r)
    dados = json.loads(txt)
    assert dados["projeto"] == "P1"
    assert dados["rt"]["R1"] == 1e-5
    # reimportavel no model
    r2 = Resultado.model_validate_json(txt)
    assert r2.estruturas[0].R1 == r.estruturas[0].R1


def test_salvar_json_escreve_arquivo(tmp_path):
    r = analisar(_projeto())
    destino = tmp_path / "res.json"
    salvar_json(r, destino)
    assert destino.exists()
    assert json.loads(destino.read_text(encoding="utf-8"))["projeto"] == "P1"
