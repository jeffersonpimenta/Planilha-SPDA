import pytest
from pydantic import ValidationError
from spda.model.projeto import (
    Projeto, Estrutura, Zona, Linha, Trecho, SistemaInterno, Medidas,
)
from spda.model.enums import (
    Localizacao, TipoConstrucao, TipoSuperficie, RiscoIncendio,
    ProvidenciaIncendio, InstalacaoLinha, TipoLinha, AmbienteLinha,
    TipoLinhaExterna,
)


def _estrutura_minima():
    return Estrutura(
        nome="Edif A", L=20, W=10, H=5,
        localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta,
        risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        n_t=100,
        zonas=[Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto,
                    n_z=50, t_z=8760, medidas=Medidas())],
    )


def test_constroi_projeto():
    p = Projeto(nome="P1", N_G=4.0, estruturas=[_estrutura_minima()])
    assert p.estruturas[0].zonas[0].n_z == 50


def test_rejeita_dimensao_negativa():
    with pytest.raises(ValidationError):
        Estrutura(
            nome="X", L=-1, W=10, H=5,
            localizacao=Localizacao.isolada,
            tipo_construcao=TipoConstrucao.robusta,
            risco_incendio=RiscoIncendio.normal,
            providencias_incendio=ProvidenciaIncendio.nenhuma,
            n_t=10, zonas=[],
        )


def test_serializa_json_roundtrip():
    p = Projeto(nome="P1", N_G=4.0, estruturas=[_estrutura_minima()])
    bruto = p.model_dump_json()
    p2 = Projeto.model_validate_json(bruto)
    assert p2 == p


def test_trecho_default_LL():
    t = Trecho()
    assert t.L_L == 1000.0
