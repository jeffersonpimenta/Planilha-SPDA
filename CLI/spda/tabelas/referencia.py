"""Valores de referencia da ABNT NBR 5419-2:2026 (defaults).

Todas as tabelas qualitativas da norma sao representadas como dados aqui. As
tabelas que dependem da tensao suportavel de impulso U_W (P_LD/B.8 e P_LI/B.9)
sao resolvidas pelos helpers `pld`/`pli`, que selecionam a coluna de U_W de forma
conservadora via `coluna_uw`. K_S4 = 1/U_W e calculado em calc.probabilidades.
"""
from spda.model.enums import (
    Localizacao, TipoConstrucao, NivelProtecao, NivelDPS, TipoSuperficie,
    RiscoIncendio, ProvidenciaIncendio, InstalacaoLinha, TipoLinha,
    AmbienteLinha, TipoLinhaExterna, ProtecaoToquePasso,
    CategoriaLinha, ClasseBlindagemRS, FiacaoInterna,
    TipoOcupacao, ZonaExplosao, PerigoEspecial,
)

# --- Numero de eventos (Anexo A) ---
C_D = {
    Localizacao.cercada_mais_altos: 0.25,
    Localizacao.cercada_mesma_altura: 0.5,
    Localizacao.isolada: 1.0,
    Localizacao.topo_colina: 2.0,
}
C_I = {
    InstalacaoLinha.aerea: 1.0,
    InstalacaoLinha.enterrada: 0.5,
    InstalacaoLinha.enterrada_malha: 0.01,
}
C_T = {
    TipoLinha.bt_sinal: 1.0,
    TipoLinha.at_trafo: 0.2,
}
C_E = {
    AmbienteLinha.rural: 1.0,
    AmbienteLinha.suburbano: 0.5,
    AmbienteLinha.urbano: 0.1,
    AmbienteLinha.urbano_alto: 0.01,
}

# --- Probabilidades (Anexo B) ---
P_TA = {
    ProtecaoToquePasso.nenhuma: 1.0,
    ProtecaoToquePasso.avisos: 0.1,
    ProtecaoToquePasso.isolacao: 0.01,
    ProtecaoToquePasso.malha_equipotencial: 0.01,
    ProtecaoToquePasso.descida_natural: 0.001,
    ProtecaoToquePasso.restricoes_fisicas: 0.0,
}
P_B = {
    NivelProtecao.nenhum: 1.0,
    NivelProtecao.IV: 0.2,
    NivelProtecao.III: 0.1,
    NivelProtecao.II: 0.05,
    NivelProtecao.I: 0.02,
    NivelProtecao.I_descida_natural: 0.01,
    NivelProtecao.captacao_descida_natural: 0.001,
}
# P_SPD (Tabela B.3): sistema coordenado de DPS. NP III e IV compartilham o
# mesmo valor. Ausencia de DPS e tratada como None no model (P_SPD = 1.0 em
# app.py). "Melhor que NP I": faixa 0.005-0.001; adotado 0.005 (conservador).
P_SPD = {
    NivelDPS.IV: 0.05,
    NivelDPS.III: 0.05,
    NivelDPS.II: 0.02,
    NivelDPS.I: 0.01,
    NivelDPS.melhor_I: 0.005,
}
C_LD = {
    TipoLinhaExterna.aerea_nao_blindada: 1.0,
    TipoLinhaExterna.subterranea_nao_blindada: 1.0,
    TipoLinhaExterna.energia_neutro_multiaterrado: 1.0,
    TipoLinhaExterna.subterranea_blindada_nao_interligada: 1.0,
    TipoLinhaExterna.aerea_blindada_nao_interligada: 1.0,
    TipoLinhaExterna.blindada_interligada: 1.0,
    TipoLinhaExterna.eletroduto_metalico: 0.0,
    TipoLinhaExterna.fibra_optica: 0.0,
    TipoLinhaExterna.interface_isolante: 0.0,
}
C_LI = {
    TipoLinhaExterna.aerea_nao_blindada: 1.0,
    TipoLinhaExterna.subterranea_nao_blindada: 1.0,
    TipoLinhaExterna.energia_neutro_multiaterrado: 0.2,
    TipoLinhaExterna.subterranea_blindada_nao_interligada: 0.3,
    TipoLinhaExterna.aerea_blindada_nao_interligada: 0.1,
    TipoLinhaExterna.blindada_interligada: 0.0,
    TipoLinhaExterna.eletroduto_metalico: 0.0,
    TipoLinhaExterna.fibra_optica: 0.0,
    TipoLinhaExterna.interface_isolante: 0.0,
}

# P_EB (Tabela B.7): ligacao equipotencial na entrada da linha, em funcao do NP
# do DPS classe I. Sem DPS -> 1.0 (tratado como None no model). Mesmos valores de B.3.
P_EB = {
    NivelDPS.IV: 0.05,
    NivelDPS.III: 0.05,
    NivelDPS.II: 0.02,
    NivelDPS.I: 0.01,
    NivelDPS.melhor_I: 0.005,
}
# P_TU (Tabela B.6): protecao contra tensao de toque na entrada da linha.
P_TU = {
    ProtecaoToquePasso.nenhuma: 1.0,
    ProtecaoToquePasso.avisos: 0.1,
    ProtecaoToquePasso.isolacao: 0.01,
    ProtecaoToquePasso.restricoes_fisicas: 0.0,
}
# K_S3 (Tabela B.5): caracteristicas da fiacao interna.
K_S3 = {
    FiacaoInterna.laco_grande: 1.0,
    FiacaoInterna.laco_medio_25: 0.5,
    FiacaoInterna.laco_medio_10: 0.2,
    FiacaoInterna.laco_pequeno: 0.01,
    FiacaoInterna.blindado_conduto: 0.0001,
}

# --- Tabelas dependentes de U_W (kV) ---
# Colunas tabuladas de tensao suportavel de impulso.
COLUNAS_UW = (1.0, 1.5, 2.5, 4.0, 6.0)
# P_LD (Tabela B.8): por condicao de blindagem/RS x coluna de U_W.
P_LD = {
    ClasseBlindagemRS.nao_blindada: {1.0: 1.0, 1.5: 1.0, 2.5: 1.0, 4.0: 1.0, 6.0: 1.0},
    ClasseBlindagemRS.rs_5_20: {1.0: 1.0, 1.5: 1.0, 2.5: 0.95, 4.0: 0.9, 6.0: 0.8},
    ClasseBlindagemRS.rs_1_5: {1.0: 0.9, 1.5: 0.8, 2.5: 0.6, 4.0: 0.3, 6.0: 0.1},
    ClasseBlindagemRS.rs_ate_1: {1.0: 0.6, 1.5: 0.4, 2.5: 0.2, 4.0: 0.04, 6.0: 0.02},
}
# P_LI (Tabela B.9): por categoria da linha x coluna de U_W.
P_LI = {
    CategoriaLinha.energia: {1.0: 1.0, 1.5: 0.6, 2.5: 0.3, 4.0: 0.16, 6.0: 0.1},
    CategoriaLinha.sinal: {1.0: 1.0, 1.5: 0.5, 2.5: 0.2, 4.0: 0.08, 6.0: 0.04},
}


def coluna_uw(uw: float | None) -> float:
    """Seleciona a coluna de U_W de forma conservadora: maior coluna <= uw.

    U_W desconhecido (None) ou < 1 kV -> coluna 1.0 (pior caso). U_W > 6 -> 6.0.
    """
    if uw is None:
        return COLUNAS_UW[0]
    elegiveis = [c for c in COLUNAS_UW if c <= uw]
    return max(elegiveis) if elegiveis else COLUNAS_UW[0]


def pld(classe: ClasseBlindagemRS, uw: float | None) -> float:
    """P_LD (B.8) para a classe de blindagem/RS e a tensao suportavel U_W."""
    return P_LD[classe][coluna_uw(uw)]


def pli(categoria: CategoriaLinha, uw: float | None) -> float:
    """P_LI (B.9) para a categoria da linha e a tensao suportavel U_W."""
    return P_LI[categoria][coluna_uw(uw)]


# --- Perdas (Anexo C) ---
R_T = {
    TipoSuperficie.terra_concreto: 1e-2,
    TipoSuperficie.marmore_ceramica: 1e-3,
    TipoSuperficie.brita_carpete: 1e-4,
    TipoSuperficie.asfalto_madeira: 1e-5,
}
# R_P (Tabela C.4): a norma tem 3 niveis; maior reducao 0.2 (instalacoes automaticas).
R_P = {
    ProvidenciaIncendio.nenhuma: 1.0,
    ProvidenciaIncendio.extintor: 0.5,
    ProvidenciaIncendio.fixo_automatico: 0.2,
}
# R_F (Tabela C.5): risco de incendio. Alto=1e-1, Normal=1e-2, Baixo=1e-3, sem risco=0.
R_F = {
    RiscoIncendio.alto: 0.1,
    RiscoIncendio.normal: 0.01,
    RiscoIncendio.baixo: 0.001,
    RiscoIncendio.sem_risco: 0.0,
}
# R_F para risco de explosao (Tabela C.5). Estrutura com zona de explosao usa
# estes valores no lugar do risco de incendio, e r_p e forcado a 1 (C.3.4).
R_F_EXPLOSAO = {
    ZonaExplosao.zona_0_20: 1.0,
    ZonaExplosao.zona_1_21: 0.1,
    ZonaExplosao.zona_2_22: 0.001,
}
R_S = {
    TipoConstrucao.simples: 2.0,
    TipoConstrucao.robusta: 1.0,
}
# H_Z (Tabela C.6): fator de aumento de perda na presenca de perigo especial.
H_Z = {
    PerigoEspecial.sem_perigo: 1.0,
    PerigoEspecial.panico_baixo: 2.0,
    PerigoEspecial.panico_medio: 5.0,
    PerigoEspecial.evacuacao_dificil: 5.0,
    PerigoEspecial.panico_alto: 10.0,
}
# Valores tipicos de vitimas (L1)
L_T = 1e-2  # D1 -- choque eletrico (todos os tipos)
L_O_PADRAO = 1e-3  # D3 -- falha de sistemas internos (outros)
L_O_EXPLOSAO = 1e-1
L_O_HOSPITAL_CRITICO = 1e-2
# L_F (D2, Tabela C.2): depende da ocupacao. Estrutura com explosao -> 0.1.
L_F = {
    TipoOcupacao.hospital: 0.1,
    TipoOcupacao.hotel: 0.1,
    TipoOcupacao.escola: 0.1,
    TipoOcupacao.edificio_civico: 0.1,
    TipoOcupacao.entretenimento: 0.05,
    TipoOcupacao.igreja: 0.05,
    TipoOcupacao.museu: 0.05,
    TipoOcupacao.industrial: 0.02,
    TipoOcupacao.comercial: 0.02,
    TipoOcupacao.outros: 0.01,
}
L_F_EXPLOSAO = 0.1   # Tabela C.2 -- L_F para estrutura com risco de explosao
L_F_L3 = 0.1         # Tabela C.9 -- L_F para patrimonio cultural (museus/galerias)

# --- Perda economica L4 (Anexo D) ---
# ATENCAO: o L4 tem tabela PROPRIA (C.12); NAO reutilizar os valores de L1 (C.2).
# L_T de L4 (C.12) = 1e-2, igual ao de L1 -> reusa L_T acima.
# L_F (D2) por ocupacao -- Tabela C.12.
L_F_L4 = {
    TipoOcupacao.hospital: 0.5,
    TipoOcupacao.industrial: 0.5,
    TipoOcupacao.museu: 0.5,
    TipoOcupacao.hotel: 0.2,
    TipoOcupacao.escola: 0.2,
    TipoOcupacao.edificio_civico: 0.2,   # escritorio/edificio civico
    TipoOcupacao.igreja: 0.2,
    TipoOcupacao.entretenimento: 0.2,
    TipoOcupacao.comercial: 0.2,
    TipoOcupacao.outros: 0.1,
}
L_F_L4_EXPLOSAO = 1.0   # Tabela C.12 -- L_F para estrutura com risco de explosao
# L_O (D3) por ocupacao -- Tabela C.12.
L_O_L4 = {
    TipoOcupacao.hospital: 0.01,
    TipoOcupacao.industrial: 0.01,
    TipoOcupacao.hotel: 0.01,
    TipoOcupacao.comercial: 0.01,
    TipoOcupacao.edificio_civico: 0.01,  # escritorio/edificio civico
    TipoOcupacao.museu: 0.001,
    TipoOcupacao.escola: 0.001,
    TipoOcupacao.igreja: 0.001,
    TipoOcupacao.entretenimento: 0.001,
    TipoOcupacao.outros: 0.0001,
}
L_O_L4_EXPLOSAO = 0.1   # Tabela C.12 -- L_O para estrutura com risco de explosao

# --- Risco toleravel / frequencia toleravel ---
# Tabela 4: R1 = 1e-5 (vida humana), R3 = 1e-4 (patrimonio cultural).
RT = {"R1": 1e-5, "R3": 1e-4, "R4": 1e-3}
# F_T (7.3.4): 0.1/ano p/ sistemas criticos (so autoridade com jurisdicao pode
# elevar); 1/ano p/ nao criticos (meramente representativo).
FT = {"critico": 0.1, "nao_critico": 1.0}
