import json
from spda.tabelas.config import carregar_tabelas


def test_sem_arquivo_usa_defaults():
    t = carregar_tabelas(None)
    assert t.RT["R1"] == 1e-5


def test_override_rt(tmp_path):
    p = tmp_path / "cfg.json"
    p.write_text(json.dumps({"RT": {"R1": 2e-5}}), encoding="utf-8")
    t = carregar_tabelas(p)
    assert t.RT["R1"] == 2e-5          # sobrescrito
    assert t.RT["R3"] == 1e-4          # preservado (Tabela 4)
