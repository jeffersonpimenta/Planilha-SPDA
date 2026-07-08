from spda.app import analisar
from spda.model.projeto import (
    Projeto, Estrutura, Zona, Linha, Trecho,
)
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie, NivelProtecao,
)
from spda.model.solucao import Solucao, SolucaoEstrutura
from spda.solucao.aplicar import aplicar_solucao


def _projeto(nivel_spda=None):
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100,
             t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200,
        nivel_spda=nivel_spda, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    return Projeto(nome="P", N_G=4.0, estruturas=[est])


def test_aplica_medida_e_reduz_r1():
    p = _projeto()
    p.solucao = Solucao(estruturas={"A": SolucaoEstrutura(medidas={"spda": "II"})})
    aplicado, avisos = aplicar_solucao(p)
    assert avisos == []
    assert aplicado.estruturas[0].nivel_spda == NivelProtecao.II
    assert p.estruturas[0].nivel_spda is None          # original intacto
    assert (analisar(aplicado).estruturas[0].R1
            < analisar(p).estruturas[0].R1)


def test_degrau_abaixo_do_instalado_prevalece_instalado():
    p = _projeto(nivel_spda=NivelProtecao.II)
    p.solucao = Solucao(estruturas={"A": SolucaoEstrutura(medidas={"spda": "IV"})})
    aplicado, avisos = aplicar_solucao(p)
    assert aplicado.estruturas[0].nivel_spda == NivelProtecao.II
    assert any("abaixo do instalado" in a for a in avisos)


def test_orfaos_geram_aviso_sem_quebrar():
    p = _projeto()
    p.solucao = Solucao(estruturas={
        "NaoExiste": SolucaoEstrutura(medidas={"spda": "II"}),
        "A": SolucaoEstrutura(medidas={"medida_fantasma": "x", "spda": "III"}),
    })
    aplicado, avisos = aplicar_solucao(p)
    assert aplicado.estruturas[0].nivel_spda == NivelProtecao.III
    assert any("NaoExiste" in a for a in avisos)
    assert any("medida_fantasma" in a for a in avisos)


def test_sem_solucao_devolve_copia_igual():
    p = _projeto()
    aplicado, avisos = aplicar_solucao(p)
    assert avisos == []
    assert aplicado.model_dump() == p.model_dump()
    assert aplicado is not p


def test_solucao_explicita_sobrepoe_a_do_projeto():
    # sandbox passa o rascunho ainda nao salvo via parametro
    p = _projeto()
    p.solucao = Solucao(estruturas={"A": SolucaoEstrutura(medidas={"spda": "IV"})})
    rascunho = Solucao(estruturas={"A": SolucaoEstrutura(medidas={"spda": "I"})})
    aplicado, _ = aplicar_solucao(p, rascunho)
    assert aplicado.estruturas[0].nivel_spda == NivelProtecao.I


def test_roundtrip_json_mantem_metricas(tmp_path):
    from spda.cli import persistencia
    p = _projeto()
    p.solucao = Solucao(estruturas={"A": SolucaoEstrutura(
        medidas={"spda": "I", "incendio": "fixo_automatico"})})
    destino = persistencia.salvar_projeto(p, tmp_path / "p.json")
    p2 = persistencia.carregar_projeto(destino)
    r1_a = analisar(aplicar_solucao(p)[0]).estruturas[0].R1
    r1_b = analisar(aplicar_solucao(p2)[0]).estruturas[0].R1
    assert r1_a == r1_b
