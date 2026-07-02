"""Conformidade com a ABNT NBR 5419-2:2026 -- testes rastreaveis a norma.

Cada teste referencia a clausula/tabela que verifica. Fontes de verdade:
norma_limpa.md (formulas) e tabelas.md (valores).
"""
from spda.app import analisar, analisar_memoria
from spda.model.enums import (
    Localizacao, NivelDPS, ProvidenciaIncendio, RiscoIncendio, TipoConstrucao,
    TipoSuperficie, TipoOcupacao, ZonaExplosao, TipoLinhaExterna,
    ClasseBlindagemRS,
)
from spda.model.projeto import Estrutura, Linha, Projeto, SistemaInterno, Zona
from spda.tabelas import referencia as ref


def _estrutura(**kw):
    zona = kw.pop("zona", None) or Zona(
        nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50, t_z=8760.0)
    base = dict(
        nome="E", L=20, W=10, H=6, localizacao=Localizacao.isolada,
        tipo_construcao=TipoConstrucao.robusta,
        risco_incendio=RiscoIncendio.normal,
        providencias_incendio=ProvidenciaIncendio.nenhuma,
        n_t=100, zonas=[zona], linhas=[Linha()],
    )
    base.update(kw)
    return Estrutura(**base)


def _analisar(est):
    return analisar(Projeto(nome="P", N_G=4.0, estruturas=[est]))


# --- B.4.9: P_M = P_SPD x P_MS quando ha DPS coordenado -------------------

def test_pm_aplica_p_spd_com_dps_coordenado():
    # Com DPS coordenado, R_M (via P_M = P_SPD*P_MS) deve cair vs. sem DPS.
    def projeto(dps):
        zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto,
                    n_z=50, t_z=8760.0,
                    sistemas_internos=[SistemaInterno(U_W=2.5, dps=dps)])
        est = _estrutura(zona=zona, sistemas_criticos=True)
        return _analisar(est)

    com_dps = projeto(NivelDPS.I).estruturas[0].zonas[0].R_M
    sem_dps = projeto(None).estruturas[0].zonas[0].R_M
    assert com_dps < sem_dps


def test_pm_uw_desconhecido_e_um():
    # B.4.10: equipamento sem U_W confirmado -> P_M = 1 (nao aplica P_SPD).
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto,
                n_z=50, t_z=8760.0,
                sistemas_internos=[SistemaInterno(U_W=None, dps=NivelDPS.I)])
    mem = analisar_memoria(Projeto(nome="P", N_G=4.0,
                                   estruturas=[_estrutura(zona=zona,
                                                          sistemas_criticos=True)]))
    assert mem.estruturas[0].zonas[0].P_M.resultado == 1.0


# --- Tabela C.2: L_F varia por ocupacao -----------------------------------

def test_lf_ocupacao_hospital_10x_outros():
    # L_F hospital=0.1 vs outros=0.01 -> R_B 10x maior.
    rb_hosp = _analisar(_estrutura(ocupacao=TipoOcupacao.hospital)
                        ).estruturas[0].zonas[0].R_B
    rb_outros = _analisar(_estrutura(ocupacao=TipoOcupacao.outros)
                          ).estruturas[0].zonas[0].R_B
    assert rb_outros > 0
    assert abs(rb_hosp / rb_outros - 10.0) < 1e-9


def test_ocupacao_default_outros():
    # Retrocompat: sem ocupacao informada -> outros (0.01), comportamento antigo.
    rb_default = _analisar(_estrutura()).estruturas[0].zonas[0].R_B
    rb_outros = _analisar(_estrutura(ocupacao=TipoOcupacao.outros)
                          ).estruturas[0].zonas[0].R_B
    assert rb_default == rb_outros


# --- Tabela C.5 / C.3.4: zona de explosao -> r_f e r_p ---------------------

def test_zona_explosao_define_rf_e_forca_rp_um():
    est = _estrutura(zona_explosao=ZonaExplosao.zona_0_20,
                     providencias_incendio=ProvidenciaIncendio.fixo_automatico)
    mem = analisar_memoria(Projeto(nome="P", N_G=4.0, estruturas=[est]))
    coefs = mem.estruturas[0].zonas[0].coefs
    assert coefs["r_f"].resultado == 1.0   # Zona 0/20
    assert coefs["r_p"].resultado == 1.0   # C.3.4: explosao -> r_p = 1


def test_zona_explosao_lf_e_lo_de_explosao():
    # Estrutura com explosao usa L_F = 0.1 mesmo com ocupacao "outros".
    rb_exp = _analisar(_estrutura(zona_explosao=ZonaExplosao.zona_1_21,
                                  risco_incendio=RiscoIncendio.baixo)
                       ).estruturas[0].zonas[0].R_B
    # r_f explosao (0.1) > r_f incendio baixo (0.001) e L_F 0.1 > 0.01 -> maior
    rb_fogo = _analisar(_estrutura(risco_incendio=RiscoIncendio.baixo)
                        ).estruturas[0].zonas[0].R_B
    assert rb_exp > rb_fogo


# --- Tabela C.12: L4 (economico) usa valores proprios, NAO os de L1/C.2 ----

def _mem_l4(**kw):
    """Memoria de uma estrutura com dados economicos (c_t/c_*) p/ ativar L4."""
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                t_z=8760.0, c_a=100.0, c_b=100.0, c_c=100.0, c_s=100.0)
    est = _estrutura(zona=zona, c_t=1000.0, **kw)
    return analisar_memoria(Projeto(nome="P", N_G=4.0, estruturas=[est]))


def test_l4_lf_usa_tabela_c12_hospital():
    # C.12 (norma:2609): L_F(hospital) p/ L4 = 0.5 (contra C.2/L1 = 0.1).
    z = _mem_l4(ocupacao=TipoOcupacao.hospital).estruturas[0].zonas[0]
    assert z.L4_B.operandos["L_F"] == 0.5


def test_l4_lo_usa_tabela_c12_comercial():
    # C.12: L_O(comercial) p/ L4 = 0.01 (contra o default L1 de 1e-3).
    z = _mem_l4(ocupacao=TipoOcupacao.comercial).estruturas[0].zonas[0]
    assert z.L4_sis.operandos["L_O"] == 0.01


def test_l4_explosao_lf_um_lo_dez_por_cento():
    # C.12: risco de explosao -> L_F = 1.0 e L_O = 0.1 no L4.
    z = _mem_l4(zona_explosao=ZonaExplosao.zona_1_21).estruturas[0].zonas[0]
    assert z.L4_B.operandos["L_F"] == 1.0
    assert z.L4_sis.operandos["L_O"] == 0.1


def test_l1_lo_permanece_c2_nao_contaminado_por_l4():
    # Regressao: L1 (L_sis) mantem L_O de C.2 (hospital critico = 0.01).
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                t_z=8760.0)
    est = _estrutura(zona=zona, sistemas_criticos=True)
    mem = analisar_memoria(Projeto(nome="P", N_G=4.0, estruturas=[est]))
    assert mem.estruturas[0].zonas[0].L_sis.operandos["L_O"] == 0.01


# --- 6.9.1.2a / 7.4.1.2a: R_W/R_Z e F_W/F_Z usam valor unico pior-caso ------

def test_pw_pz_usam_pior_caso_nao_combinam_sistemas():
    # Dois sistemas identicos (P_SPD=0.02, P_LD=1, C_LD=1) -> P_W_i = 0.02.
    # Norma: valor unico pior-caso (0.02). Combinacao daria 1-0.98^2 = 0.0396.
    def sis():
        return SistemaInterno(U_W=6.0, dps=NivelDPS.II)
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                t_z=8760.0, sistemas_internos=[sis(), sis()])
    est = _estrutura(zona=zona, sistemas_criticos=True)
    linha = analisar_memoria(
        Projeto(nome="P", N_G=4.0, estruturas=[est])
    ).estruturas[0].zonas[0].linhas[0]
    # P_W_i = P_SPD*P_LD*C_LD = 0.02*1*1 = 0.02.
    assert abs(linha.P_W.resultado - 0.02) < 1e-12
    # P_Z_i = P_SPD*P_LI*C_LI = 0.02*0.1*1 = 0.002 (P_LI energia @6kV = 0.1).
    assert abs(linha.P_Z.resultado - 0.002) < 1e-12


# --- Nota Eqs D.1-D.4 (norma:2635): R_T representativo -> razoes c/c_t = 1 --

def test_r4_representativo_forca_razoes_um():
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                t_z=8760.0, c_a=100.0, c_b=100.0, c_c=100.0, c_s=100.0)
    est = _estrutura(zona=zona, c_t=1000.0)

    def l4a(repr4):
        return analisar_memoria(
            Projeto(nome="P", N_G=4.0, estruturas=[est],
                    r4_representativo=repr4)).estruturas[0].zonas[0].L4_A

    # Detalhado: razao c_a/c_t = 100/1000 = 0.1. Representativo: razao = 1 -> 10x.
    assert abs(l4a(True).resultado / l4a(False).resultado - 10.0) < 1e-9


# --- 7.3.4: frequencia toleravel F_T ----------------------------------------

def test_ft_nao_critico_um_por_ano():
    # F_T = 1/ano para sistemas nao criticos (representativo).
    assert _analisar(_estrutura()).estruturas[0].ft == 1.0


def test_ft_critico_um_decimo_por_ano():
    # F_T = 0.1/ano para sistemas criticos (nao pode ser alterado).
    assert _analisar(_estrutura(sistemas_criticos=True)).estruturas[0].ft == 0.1


def test_ft_override_prevalece():
    r = analisar(Projeto(nome="P", N_G=4.0, ft_override=0.5,
                         estruturas=[_estrutura(sistemas_criticos=True)]))
    assert r.estruturas[0].ft == 0.5


# --- Tabela 7: F_V = (N_L + N_DJ) x P_EB ------------------------------------

def test_fv_usa_p_eb_nao_p_v():
    # Linha blindada rs<=1 com U_W=6 kV: P_V = P_EB*P_LD*C_LD = 0.02, mas
    # P_EB = 1 (sem DPS de entrada). A parcela F_V deve ser N_L_total * P_EB.
    zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                t_z=8760.0, sistemas_internos=[SistemaInterno(U_W=6.0)])
    linha = Linha(tipo_externa=TipoLinhaExterna.blindada_interligada,
                  classe_blindagem=ClasseBlindagemRS.rs_ate_1)
    est = _estrutura(zona=zona, linhas=[linha])
    me = analisar_memoria(
        Projeto(nome="P", N_G=4.0, estruturas=[est])).estruturas[0]
    mz = me.zonas[0]
    ml = mz.linhas[0]
    assert ml.P_EB.resultado != ml.P_V.resultado  # o cenario distingue os dois
    esperado = (me.N_D.resultado * mz.P_C.resultado
                + me.N_M.resultado * mz.P_M.resultado
                + ml.N_L_total * ml.P_EB.resultado
                + ml.N_L_total * ml.P_W.resultado
                + ml.N_I_total * ml.P_Z.resultado)
    assert abs(mz.F_zona.resultado - esperado) < 1e-15


# --- Tabela 7, nota a: F_B so com equipamento em ZPR 0A ----------------------

def test_fb_somado_apenas_com_equipamento_zpr0a():
    def me(em0a):
        zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                    t_z=8760.0,
                    sistemas_internos=[SistemaInterno(U_W=2.5, em_zpr0a=em0a)])
        return analisar_memoria(
            Projeto(nome="P", N_G=4.0, estruturas=[_estrutura(zona=zona)])
        ).estruturas[0]

    sem, com = me(False), me(True)
    # Sem SPDA, P_B = 1 -> F_B = N_D. A diferenca de F deve ser exatamente N_D.
    assert abs((com.F.resultado - sem.F.resultado) - com.N_D.resultado) < 1e-15


# --- Tabela C.2 (L_O de hospital): D3 entra em R1 p/ ocupacao hospital -------

def test_hospital_inclui_d3_em_r1():
    def dominantes(ocup):
        zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                    t_z=8760.0, sistemas_internos=[SistemaInterno(U_W=2.5)])
        re = _analisar(_estrutura(zona=zona, ocupacao=ocup)).estruturas[0]
        return [nome for nome, _ in re.dominantes]

    assert "R_C" in dominantes(TipoOcupacao.hospital)
    assert "R_C" not in dominantes(TipoOcupacao.outros)


# --- Tabela C.12: no modo representativo, L4 D1 so onde ha animais -----------

def test_l4a_representativo_sem_animais_e_zero():
    def l4a(c_a):
        zona = Zona(nome="Z", superficie=TipoSuperficie.terra_concreto, n_z=50,
                    t_z=8760.0, c_a=c_a)
        est = _estrutura(zona=zona, c_t=1000.0)
        return analisar_memoria(
            Projeto(nome="P", N_G=4.0, estruturas=[est], r4_representativo=True)
        ).estruturas[0].zonas[0].L4_A

    assert l4a(None).resultado == 0.0
    assert abs(l4a(100.0).resultado - 1e-2 * 1e-2) < 1e-18


# --- Tabelas B.3/B.7: DPS melhor que NP I ------------------------------------

def test_dps_melhor_que_np_i():
    assert ref.P_SPD[NivelDPS.melhor_I] == 0.005
    assert ref.P_EB[NivelDPS.melhor_I] == 0.005


# --- Rastreabilidade: numeracao do Anexo A (eq. A.3; Tabelas A.2/A.4) --------

def test_rotulos_anexo_a():
    me = analisar_memoria(
        Projeto(nome="P", N_G=4.0, estruturas=[_estrutura()])).estruturas[0]
    assert me.N_D.eq == "A.3"          # A.2 e a saliencia A'_D, nao o N_D
    tr = me.zonas[0].linhas[0].trechos[0]
    assert tr.C_I.eq == "Tabela A.2"
    assert tr.C_E.eq == "Tabela A.4"
