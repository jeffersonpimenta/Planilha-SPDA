from spda.model.projeto import Projeto, Estrutura, Zona
from spda.model.solucao import Solucao, SolucaoEstrutura
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)


def _projeto():
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=10, t_z=8760)
    est = Estrutura(
        nome="A", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=20, zonas=[z],
    )
    return Projeto(nome="P", N_G=2.0, estruturas=[est])


def test_projeto_sem_solucao_carrega_como_none():
    p = _projeto()
    assert p.solucao is None
    # JSON antigo (sem o campo) tambem carrega
    bruto = p.model_dump_json(exclude={"solucao"})
    assert Projeto.model_validate_json(bruto).solucao is None


def test_solucao_roundtrip_json():
    p = _projeto()
    p.solucao = Solucao(estruturas={
        "A": SolucaoEstrutura(medidas={"spda": "III", "fiacao": "0.2"}),
    })
    p2 = Projeto.model_validate_json(p.model_dump_json())
    assert p2.solucao.estruturas["A"].medidas == {"spda": "III", "fiacao": "0.2"}
    assert p2 == p
