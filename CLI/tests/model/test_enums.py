from spda.model.enums import (
    Localizacao, TipoConstrucao, NivelProtecao, TipoSuperficie,
    RiscoIncendio, ProvidenciaIncendio, InstalacaoLinha, TipoLinha,
    AmbienteLinha, RelevanciaAD, TipoLinhaExterna, ProtecaoToquePasso,
)

def test_enums_sao_strings():
    assert Localizacao.isolada.value == "isolada"
    assert NivelProtecao.I.value == "I"

def test_cobertura_minima():
    assert len(list(Localizacao)) == 4
    assert len(list(NivelProtecao)) == 7
    assert TipoConstrucao.simples in TipoConstrucao
