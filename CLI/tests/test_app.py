import math
from spda.app import analisar
from spda.model.projeto import (
    Projeto, Estrutura, Zona, Linha, Trecho, Medidas, SistemaInterno,
    EstruturaAdjacente,
)
from spda.model.enums import (
    Localizacao, TipoConstrucao, TipoSuperficie, RiscoIncendio,
    ProvidenciaIncendio, NivelProtecao, NivelDPS, TipoLinha, InstalacaoLinha,
    AmbienteLinha, TipoLinhaExterna, ProtecaoToquePasso,
    CategoriaLinha, ClasseBlindagemRS,
)


def _projeto():
    zona = Zona(
        nome="Z1", superficie=TipoSuperficie.terra_concreto,
        n_z=50, t_z=8760,
        medidas=Medidas(protecao_toque_passo=ProtecaoToquePasso.nenhuma),
    )
    est = Estrutura(
        nome="Edif A", L=20, W=10, H=5,
        localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta,
        risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        nivel_spda=None, n_t=100, zonas=[zona],
        linhas=[Linha(tipo=TipoLinha.bt_sinal, trechos=[Trecho(L_L=1000)])],
    )
    return Projeto(nome="P1", N_G=4.0, estruturas=[est])


def test_analisar_retorna_resultado():
    r = analisar(_projeto())
    assert r.projeto == "P1"
    assert len(r.estruturas) == 1
    re = r.estruturas[0]
    # N_D = 4 * area_AD(20,10,5) * 1 * 1e-6
    area = 200 + 6 * 5 * 30 + 9 * math.pi * 25
    assert abs(re.N_D - 4 * area * 1e-6) < 1e-12
    assert re.R1 > 0
    # R1 deve refletir comparacao com RT (1e-5)
    assert re.excede_R1 == (re.R1 > 1e-5)


def test_flag_explosao_aumenta_R1():
    p_sem = _projeto()
    r_sem = analisar(p_sem)
    p_com = _projeto()
    p_com.estruturas[0].risco_explosao = True
    # adiciona um sistema interno p/ gerar R_C/R_M nao nulos
    p_com.estruturas[0].zonas[0].sistemas_internos = [
        SistemaInterno(U_W=2.5, K_S1=0.5, K_S2=0.5)
    ]
    r_com = analisar(p_com)
    assert r_com.estruturas[0].R1 >= r_sem.estruturas[0].R1


def _zona(**kw):
    base = dict(nome="Z1", superficie=TipoSuperficie.terra_concreto,
                n_z=50, t_z=8760)
    base.update(kw)
    return Zona(**base)


def _estrutura(zona, **kw):
    base = dict(
        nome="A", L=20, W=10, H=5,
        localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta,
        risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        n_t=100, zonas=[zona],
    )
    base.update(kw)
    return Estrutura(**base)


def test_NDJ_contado_uma_vez_independe_da_divisao_em_trechos():
    # N_L e linear em L_L e N_DJ e por linha -> R_U de 1x1000m == 2x500m.
    adj = EstruturaAdjacente(L_J=20, W_J=10, H_J=5)

    def projeto(trechos):
        est = _estrutura(_zona(), linhas=[Linha(adjacente=adj, trechos=trechos)])
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    ru_1 = analisar(projeto([Trecho(L_L=1000)])).estruturas[0].zonas[0].R_U
    ru_2 = analisar(
        projeto([Trecho(L_L=500), Trecho(L_L=500)])
    ).estruturas[0].zonas[0].R_U
    assert ru_1 > 0
    assert abs(ru_1 - ru_2) < 1e-15


def test_NDJ_por_linha_nao_superconta():
    # N_DJ pertence a linha que conecta a adjacente: por uma linha entra 1x, nao
    # em todas. Antes (adjacente por Estrutura) a mesma adjacente entrava em toda linha.
    adj = EstruturaAdjacente(L_J=20, W_J=10, H_J=5)

    def projeto(adjs):
        linhas = [Linha(adjacente=a) for a in adjs]
        est = _estrutura(_zona(), linhas=linhas)
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    r0 = analisar(projeto([None, None])).estruturas[0].zonas[0].R_U
    r1 = analisar(projeto([adj, None])).estruturas[0].zonas[0].R_U
    r2 = analisar(projeto([adj, adj])).estruturas[0].zonas[0].R_U
    assert r0 < r1 < r2                       # cada adjacente entra 1x, na sua linha
    assert abs((r1 - r0) - (r2 - r1)) < 1e-18  # incremento igual (linhas identicas)


def test_F_nao_duplica_FC_FM_por_linha():
    # F_C e F_M sao por zona; com 2 linhas F nao pode ser o dobro de 1 linha.
    def projeto(n_linhas):
        zona = _zona(
            sistemas_internos=[SistemaInterno(U_W=2.5, K_S1=0.5, K_S2=0.5)]
        )
        est = _estrutura(zona, sistemas_criticos=True,
                         linhas=[Linha() for _ in range(n_linhas)])
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    f1 = analisar(projeto(1)).estruturas[0].F
    f2 = analisar(projeto(2)).estruturas[0].F
    assert f1 > 0
    assert f2 < 2 * f1 - 1e-12


def test_F_conta_FC_FM_mesmo_sem_linhas():
    zona = _zona(sistemas_internos=[SistemaInterno(U_W=2.5, K_S1=0.5, K_S2=0.5)])
    est = _estrutura(zona, sistemas_criticos=True, linhas=[])
    r = analisar(Projeto(nome="P", N_G=4.0, estruturas=[est]))
    assert r.estruturas[0].F > 0


def test_R3_patrimonio_estrutura_e_linha():
    zona = _zona(c_z=500)
    est = _estrutura(zona, c_t=1000, linhas=[Linha()])
    re = analisar(Projeto(nome="P", N_G=4.0, estruturas=[est])).estruturas[0]
    assert re.R3 > 0
    assert re.zonas[0].R_B3 > 0
    assert re.zonas[0].R_V3 > 0


def test_R4_inclui_componentes_de_linha():
    # c_b (valor da edificacao) gera R_B4 (estrutura) e R_V4 (linha).
    def projeto(com_linha):
        zona = _zona(c_b=800)
        est = _estrutura(zona, c_t=1000, linhas=[Linha()] if com_linha else [])
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    r_sem = analisar(projeto(False)).estruturas[0].R4
    r_com = analisar(projeto(True)).estruturas[0].R4
    assert r_sem > 0
    assert r_com > r_sem


def test_dps_sistema_valido_nao_quebra():
    zona = _zona(sistemas_internos=[SistemaInterno(U_W=2.5, dps=NivelDPS.II)])
    est = _estrutura(zona, sistemas_criticos=True, linhas=[Linha()])
    r = analisar(Projeto(nome="P", N_G=4.0, estruturas=[est]))
    assert r.estruturas[0].R1 >= 0


def test_uw_maior_reduz_risco_via_PLD_e_KS4():
    # Linha blindada interligada (RS<=1): P_LD e K_S4 caem com U_W, entao
    # R_U/R_W/R_M (e R1) caem quando U_W sobe de 1 p/ 6 kV.
    def projeto(uw):
        zona = _zona(sistemas_internos=[SistemaInterno(U_W=uw, K_S1=0.5, K_S2=0.5)])
        linha = Linha(categoria=CategoriaLinha.energia,
                      tipo_externa=TipoLinhaExterna.blindada_interligada,
                      classe_blindagem=ClasseBlindagemRS.rs_ate_1)
        est = _estrutura(zona, sistemas_criticos=True, linhas=[linha])
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    r_baixo = analisar(projeto(1.0)).estruturas[0]
    r_alto = analisar(projeto(6.0)).estruturas[0]
    assert r_alto.R1 < r_baixo.R1
    assert r_alto.zonas[0].R_U < r_baixo.zonas[0].R_U   # P_LD 0.02 vs 0.6
    assert r_alto.zonas[0].R_W < r_baixo.zonas[0].R_W
    assert r_alto.zonas[0].R_M < r_baixo.zonas[0].R_M   # K_S4 1/6 vs 1


def test_uw_maior_reduz_RZ_via_PLI():
    # Linha com C_LI>0 (neutro multiaterrado): P_LI cai com U_W -> R_Z cai.
    def projeto(uw):
        zona = _zona(sistemas_internos=[SistemaInterno(U_W=uw)])
        linha = Linha(categoria=CategoriaLinha.energia,
                      tipo_externa=TipoLinhaExterna.energia_neutro_multiaterrado)
        est = _estrutura(zona, sistemas_criticos=True, linhas=[linha])
        return Projeto(nome="P", N_G=4.0, estruturas=[est])

    r_baixo = analisar(projeto(1.0)).estruturas[0]
    r_alto = analisar(projeto(6.0)).estruturas[0]
    assert r_baixo.zonas[0].R_Z > 0
    assert r_alto.zonas[0].R_Z < r_baixo.zonas[0].R_Z   # P_LI 0.1 vs 1.0


def test_resultado_carrega_rt_e_ft():
    r = analisar(_projeto())
    assert r.rt["R1"] == 1e-5
    assert r.rt["R3"] == 1e-4
    assert r.rt["R4"] == 1e-3
    # 7.3.4: F_T por estrutura -- 1/ano (nao critico) vs 0.1/ano (critico).
    assert r.estruturas[0].ft == 1.0


def test_rt_override_reflete_no_resultado():
    p = _projeto()
    p.rt_override = {"R1": 5e-5}
    r = analisar(p)
    assert r.rt["R1"] == 5e-5
    # chaves nao sobrescritas mantem default
    assert r.rt["R3"] == 1e-4
