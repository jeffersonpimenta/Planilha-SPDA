from spda.model.enums import (
    Localizacao, TipoSuperficie, NivelProtecao, TipoLinhaExterna, TipoConstrucao,
    RiscoIncendio, ProvidenciaIncendio, CategoriaLinha, ClasseBlindagemRS,
    TipoOcupacao, ZonaExplosao,
)
from spda.tabelas import referencia as ref


def test_C_D():
    assert ref.C_D[Localizacao.isolada] == 1
    assert ref.C_D[Localizacao.topo_colina] == 2


def test_r_t():
    assert ref.R_T[TipoSuperficie.terra_concreto] == 1e-2
    assert ref.R_T[TipoSuperficie.asfalto_madeira] == 1e-5


def test_P_B():
    assert ref.P_B[NivelProtecao.nenhum] == 1
    assert ref.P_B[NivelProtecao.I] == 0.02
    assert ref.P_B[NivelProtecao.captacao_descida_natural] == 0.001


def test_C_LD_C_LI():
    assert ref.C_LD[TipoLinhaExterna.aerea_nao_blindada] == 1
    assert ref.C_LI[TipoLinhaExterna.blindada_interligada] == 0
    assert ref.C_LI[TipoLinhaExterna.energia_neutro_multiaterrado] == 0.2


def test_r_s():
    assert ref.R_S[TipoConstrucao.simples] == 2
    assert ref.R_S[TipoConstrucao.robusta] == 1


def test_RT():
    # Tabela 4: R1 = 1e-5, R3 = 1e-4 (perda de patrimonio cultural).
    assert ref.RT["R1"] == 1e-5
    assert ref.RT["R3"] == 1e-4
    assert ref.RT["R4"] == 1e-3


def test_L_F_ocupacao():
    # Tabela C.2 (D2): L_F por tipo de ocupacao.
    assert ref.L_F[TipoOcupacao.hospital] == 0.1
    assert ref.L_F[TipoOcupacao.escola] == 0.1
    assert ref.L_F[TipoOcupacao.museu] == 0.05
    assert ref.L_F[TipoOcupacao.industrial] == 0.02
    assert ref.L_F[TipoOcupacao.outros] == 0.01


def test_R_F_explosao():
    # Tabela C.5: Zonas 0/20 -> 1, 1/21 -> 0.1, 2/22 -> 1e-3.
    assert ref.R_F_EXPLOSAO[ZonaExplosao.zona_0_20] == 1.0
    assert ref.R_F_EXPLOSAO[ZonaExplosao.zona_1_21] == 0.1
    assert ref.R_F_EXPLOSAO[ZonaExplosao.zona_2_22] == 0.001


def test_L_F_L3():
    # Tabela C.9: L_F para patrimonio cultural (museus/galerias) = 0.1.
    assert ref.L_F_L3 == 0.1


def test_r_f_corrigido():
    # Tabela C.5: alto=0.1, normal=0.01, baixo=0.001, sem risco=0.
    assert ref.R_F[RiscoIncendio.alto] == 0.1
    assert ref.R_F[RiscoIncendio.normal] == 0.01
    assert ref.R_F[RiscoIncendio.baixo] == 0.001
    assert ref.R_F[RiscoIncendio.sem_risco] == 0.0


def test_r_p_sem_nivel_extra():
    # Tabela C.4: 3 niveis; maior reducao 0.2 (sem o antigo 0.1).
    assert ref.R_P[ProvidenciaIncendio.fixo_automatico] == 0.2
    assert min(ref.R_P.values()) == 0.2
    assert not hasattr(ProvidenciaIncendio, "fixo_hidrante")


def test_coluna_uw_conservadora():
    assert ref.coluna_uw(None) == 1.0     # desconhecido -> pior caso
    assert ref.coluna_uw(0.5) == 1.0      # < 1 kV -> 1
    assert ref.coluna_uw(4.0) == 4.0      # exato
    assert ref.coluna_uw(3.0) == 2.5      # arredonda p/ baixo (conservador)
    assert ref.coluna_uw(10.0) == 6.0     # > 6 -> 6


def test_pld_tabela_B8():
    assert ref.pld(ClasseBlindagemRS.nao_blindada, 6.0) == 1.0
    assert ref.pld(ClasseBlindagemRS.rs_ate_1, 6.0) == 0.02
    assert ref.pld(ClasseBlindagemRS.rs_1_5, 2.5) == 0.6
    assert ref.pld(ClasseBlindagemRS.rs_ate_1, None) == 0.6   # coluna 1 kV


def test_pli_tabela_B9():
    assert ref.pli(CategoriaLinha.energia, 6.0) == 0.1
    assert ref.pli(CategoriaLinha.sinal, 2.5) == 0.2
    assert ref.pli(CategoriaLinha.energia, 1.0) == 1.0
