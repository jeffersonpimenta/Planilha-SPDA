from spda.model.identificacao import Identificacao
from spda.model.projeto import Projeto


def test_identificacao_defaults():
    ident = Identificacao()
    assert ident.norma == "ABNT NBR 5419-2"
    assert ident.revisao == "2026"
    assert ident.responsavel is None
    assert ident.art is None
    assert ident.registro is None


def test_identificacao_preenchida():
    ident = Identificacao(responsavel="Eng. Fulano", art="123/2026",
                          registro="CREA-MG 12345")
    assert ident.art == "123/2026"
    assert ident.registro == "CREA-MG 12345"


def test_projeto_aceita_identificacao():
    p = Projeto(nome="P", N_G=1.0, identificacao=Identificacao(cliente="ACME"))
    assert p.identificacao.cliente == "ACME"


def test_projeto_identificacao_default_none():
    p = Projeto(nome="P", N_G=1.0)
    assert p.identificacao is None
