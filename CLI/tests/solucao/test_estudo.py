from spda.app import analisar
from spda.solucao.estudo import estudo_solucao
from spda.model.projeto import (
    Projeto, Estrutura, Zona, Linha, Trecho, SistemaInterno,
)
from spda.model.enums import (
    Localizacao, TipoConstrucao, RiscoIncendio, ProvidenciaIncendio,
    TipoSuperficie,
)


def _projeto_arriscado():
    # estrutura sem SPDA, muita gente, longa exposicao -> R1 > RT
    z = Zona(nome="Z1", superficie=TipoSuperficie.terra_concreto, n_z=100, t_z=8760)
    est = Estrutura(
        nome="A", L=50, W=30, H=20, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.simples, risco_incendio=RiscoIncendio.alto,
        providencias_incendio=ProvidenciaIncendio.nenhuma, n_t=200, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    return Projeto(nome="P", N_G=4.0, estruturas=[est])


def test_estudo_so_inclui_estruturas_que_excedem():
    p = _projeto_arriscado()
    assert analisar(p).estruturas[0].excede_R1
    est_sol = estudo_solucao(p)
    assert len(est_sol.estruturas) == 1
    assert est_sol.estruturas[0].nome == "A"


def test_estudo_vazio_quando_nao_excede():
    # estrutura mansa: pouca gente, pouca exposicao
    z = Zona(nome="Z1", superficie=TipoSuperficie.asfalto_madeira, n_z=1, t_z=10)
    est = Estrutura(
        nome="B", L=10, W=10, H=3, localizacao=Localizacao.cercada_mais_altos,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.baixo,
        providencias_incendio=ProvidenciaIncendio.fixo_automatico, n_t=2, zonas=[z],
    )
    p = Projeto(nome="P", N_G=1.0, estruturas=[est])
    assert not analisar(p).estruturas[0].excede_R1
    assert estudo_solucao(p).estruturas == []


def test_estudo_reduz_R1_monotonicamente():
    est_sol = estudo_solucao(_projeto_arriscado())
    e = est_sol.estruturas[0]
    rs = [p.R_projetado for p in e.passos]
    assert rs == sorted(rs, reverse=True)  # cada passo reduz (ou mantem) R1
    assert e.R1_final <= e.R1_inicial
    assert e.passos  # propos ao menos uma medida


def test_estudo_marca_atingiu_rt():
    est_sol = estudo_solucao(_projeto_arriscado())
    e = est_sol.estruturas[0]
    if e.atingiu_rt:
        assert e.R1_final <= e.rt_R1
        assert e.passos[-1].atingiu_rt
    else:
        # esgotou medidas sem atingir: reporta menor R alcancado
        assert e.R1_final > e.rt_R1


def test_passo_descreve_de_para():
    e = estudo_solucao(_projeto_arriscado()).estruturas[0]
    p0 = e.passos[0]
    assert p0.medida and p0.parametro
    assert p0.de != p0.para


def _projeto_so_F_excede():
    # Poucas pessoas/exposicao -> R1 baixo; sistema interno sem DPS e U_W baixo,
    # muitos eventos -> F (frequencia) alta. F independe da ocupacao (perdas).
    sis = SistemaInterno(nome="S", U_W=1.0)  # sem DPS -> P_C/P_W/P_Z altos
    z = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=1, t_z=1,
             sistemas_internos=[sis])
    est = Estrutura(
        nome="C", L=80, W=80, H=30, localizacao=Localizacao.topo_colina,
        tipo_construcao=TipoConstrucao.robusta, risco_incendio=RiscoIncendio.baixo,
        providencias_incendio=ProvidenciaIncendio.fixo_automatico,
        sistemas_criticos=True, n_t=1000, zonas=[z],
        linhas=[Linha(trechos=[Trecho(L_L=1000)])],
    )
    return Projeto(nome="P", N_G=10.0, estruturas=[est])


def test_estudo_inclui_estrutura_que_so_excede_F():
    p = _projeto_so_F_excede()
    re = analisar(p).estruturas[0]
    assert re.excede_F  # foco do teste: F excede
    est_sol = estudo_solucao(p)
    assert [e.nome for e in est_sol.estruturas] == ["C"]
    e = est_sol.estruturas[0]
    assert e.F_final <= e.F_inicial   # medidas (DPS) reduzem F
    assert e.passos                    # propos ao menos uma medida (DPS)
