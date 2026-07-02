from enum import Enum


class Localizacao(str, Enum):
    cercada_mais_altos = "cercada_mais_altos"      # C_D = 0.25
    cercada_mesma_altura = "cercada_mesma_altura"  # C_D = 0.5
    isolada = "isolada"                            # C_D = 1
    topo_colina = "topo_colina"                    # C_D = 2


class TipoConstrucao(str, Enum):
    simples = "simples"   # r_s = 2 (madeira/alvenaria)
    robusta = "robusta"   # r_s = 1 (metalica/concreto armado)


class NivelProtecao(str, Enum):
    nenhum = "nenhum"
    IV = "IV"
    III = "III"
    II = "II"
    I = "I"
    I_descida_natural = "I_descida_natural"            # P_B = 0.01
    captacao_descida_natural = "captacao_descida_natural"  # P_B = 0.001


class NivelDPS(str, Enum):
    """Nivel do sistema coordenado de DPS (P_SPD, Tabela B.3)."""
    IV = "IV"
    III = "III"
    II = "II"
    I = "I"
    melhor_I = "melhor_I"   # DPS melhor que NP I -> 0.005 (faixa 0.005-0.001)


class TipoSuperficie(str, Enum):
    terra_concreto = "terra_concreto"      # r_t = 1e-2
    marmore_ceramica = "marmore_ceramica"  # r_t = 1e-3
    brita_carpete = "brita_carpete"        # r_t = 1e-4
    asfalto_madeira = "asfalto_madeira"    # r_t = 1e-5


class RiscoIncendio(str, Enum):
    # Tabela C.5 (incendio): alto=0.1, normal=0.01, baixo=0.001, sem risco=0.
    alto = "alto"            # r_f = 0.1
    normal = "normal"        # r_f = 0.01
    baixo = "baixo"          # r_f = 0.001
    sem_risco = "sem_risco"  # r_f = 0


class ZonaExplosao(str, Enum):
    """Tabela C.5 (explosao) -- define r_f e forca r_p = 1 (C.3.4)."""
    nenhuma = "nenhuma"      # sem risco de explosao -> usa RiscoIncendio
    zona_0_20 = "zona_0_20"  # Zonas 0, 20 e explosivos solidos -> r_f = 1
    zona_1_21 = "zona_1_21"  # Zonas 1, 21 -> r_f = 0.1
    zona_2_22 = "zona_2_22"  # Zonas 2, 22 -> r_f = 0.001


class TipoOcupacao(str, Enum):
    """Tabela C.2 (D2) -- L_F em funcao do uso/ocupacao da estrutura."""
    hospital = "hospital"                # L_F = 0.1
    hotel = "hotel"                      # L_F = 0.1
    escola = "escola"                    # L_F = 0.1
    edificio_civico = "edificio_civico"  # L_F = 0.1
    entretenimento = "entretenimento"    # L_F = 0.05
    igreja = "igreja"                    # L_F = 0.05
    museu = "museu"                      # L_F = 0.05
    industrial = "industrial"            # L_F = 0.02
    comercial = "comercial"              # L_F = 0.02
    outros = "outros"                    # L_F = 0.01


class ProvidenciaIncendio(str, Enum):
    # Tabela C.4 -- a norma tem 3 niveis; a maior reducao e 0.2 (instalacoes
    # automaticas). "extintor" agrupa as providencias manuais (extintores,
    # hidrantes, alarmes manuais, rotas de escape -> r_p = 0.5).
    nenhuma = "nenhuma"                  # r_p = 1
    extintor = "extintor"                # r_p = 0.5
    fixo_automatico = "fixo_automatico"  # r_p = 0.2


class ProtecaoToquePasso(str, Enum):
    nenhuma = "nenhuma"                  # P_TA = 1
    avisos = "avisos"                    # P_TA = 0.1
    isolacao = "isolacao"                # P_TA = 0.01
    malha_equipotencial = "malha_equipotencial"  # P_TA = 0.01
    descida_natural = "descida_natural"  # P_TA = 0.001
    restricoes_fisicas = "restricoes_fisicas"    # P_TA = 0


class InstalacaoLinha(str, Enum):
    aerea = "aerea"                      # C_I = 1
    enterrada = "enterrada"              # C_I = 0.5
    enterrada_malha = "enterrada_malha"  # C_I = 0.01


class TipoLinha(str, Enum):
    bt_sinal = "bt_sinal"  # C_T = 1
    at_trafo = "at_trafo"  # C_T = 0.2


class AmbienteLinha(str, Enum):
    rural = "rural"            # C_E = 1
    suburbano = "suburbano"    # C_E = 0.5
    urbano = "urbano"          # C_E = 0.1
    urbano_alto = "urbano_alto"  # C_E = 0.01 (urbano c/ edif. > 20 m)


class TipoLinhaExterna(str, Enum):
    """Determina C_LD e C_LI (Secao 6.9)."""
    aerea_nao_blindada = "aerea_nao_blindada"            # C_LD=1, C_LI=1
    subterranea_nao_blindada = "subterranea_nao_blindada"  # C_LD=1, C_LI=1
    energia_neutro_multiaterrado = "energia_neutro_multiaterrado"  # C_LD=1, C_LI=0.2
    subterranea_blindada_nao_interligada = "subterranea_blindada_nao_interligada"  # C_LD=1, C_LI=0.3
    aerea_blindada_nao_interligada = "aerea_blindada_nao_interligada"  # C_LD=1, C_LI=0.1
    blindada_interligada = "blindada_interligada"        # C_LD=1, C_LI=0
    eletroduto_metalico = "eletroduto_metalico"          # C_LD=0, C_LI=0
    fibra_optica = "fibra_optica"                        # C_LD=0, C_LI=0
    interface_isolante = "interface_isolante"            # C_LD=0, C_LI=0


class CategoriaLinha(str, Enum):
    """Energia vs. sinal -- define a coluna da Tabela B.9 (P_LI)."""
    energia = "energia"  # P_LI: 1 / 0.6 / 0.3 / 0.16 / 0.1
    sinal = "sinal"      # P_LI: 1 / 0.5 / 0.2 / 0.08 / 0.04


class ClasseBlindagemRS(str, Enum):
    """Condicao de roteamento/blindagem/RS do cabo -- linha da Tabela B.8 (P_LD)."""
    nao_blindada = "nao_blindada"  # nao blindada ou blindagem nao interligada -> P_LD=1
    rs_5_20 = "rs_5_20"            # blindada interligada, 5 < RS <= 20 ohm/km
    rs_1_5 = "rs_1_5"             # blindada interligada, 1 < RS <= 5 ohm/km
    rs_ate_1 = "rs_ate_1"         # blindada interligada, RS <= 1 ohm/km


class FiacaoInterna(str, Enum):
    """Tipo de fiacao interna -- Tabela B.5 (K_S3)."""
    laco_grande = "laco_grande"          # cabo nao blindado, laco ~50 m2 -> 1
    laco_medio_25 = "laco_medio_25"      # ~25 m2 -> 0.5
    laco_medio_10 = "laco_medio_10"      # ~10 m2 -> 0.2
    laco_pequeno = "laco_pequeno"        # ~0.5 m2 -> 0.01
    blindado_conduto = "blindado_conduto"  # cabo blindado / conduto metalico -> 0.0001


class RelevanciaAD(str, Enum):
    estrutura_inteira = "estrutura_inteira"
    parte_hmin = "parte_hmin"
    parte_hmax = "parte_hmax"


class PerigoEspecial(str, Enum):
    """Tabela C.6 -- fator h_z de aumento de perda por perigo especial."""
    sem_perigo = "sem_perigo"                # h_z = 1
    panico_baixo = "panico_baixo"            # h_z = 2  (<= 2 andares, <= 100 pessoas)
    panico_medio = "panico_medio"            # h_z = 5  (eventos com 100-1000 pessoas)
    evacuacao_dificil = "evacuacao_dificil"  # h_z = 5  (imobilizados, hospitais)
    panico_alto = "panico_alto"              # h_z = 10 (eventos com > 1000 pessoas)


# --- Rotulos legiveis (proximos aos termos da ABNT NBR 5419-2:2026) ---
# Os values dos enums (curtos, com "_") persistem em JSON; estes rotulos sao
# apenas de APRESENTACAO (escolhas da CLI e campo `origem` do memorial). A tabela
# de origem esta indicada em comentario.
ROTULOS: dict[Enum, str] = {
    # Tabela A.1 -- fator de localizacao C_D
    Localizacao.cercada_mais_altos: "Estrutura cercada por objetos mais altos",
    Localizacao.cercada_mesma_altura: "Estrutura cercada por objetos da mesma altura ou mais baixos",
    Localizacao.isolada: "Estrutura isolada (nenhum objeto nas vizinhanças)",
    Localizacao.topo_colina: "Estrutura isolada no topo de uma colina ou monte",
    # Tabela C.7 -- fator r_s (tipo de estrutura)
    TipoConstrucao.simples: "Simples: madeira ou alvenaria simples",
    TipoConstrucao.robusta: "Robusta: estrutura metálica ou concreto armado",
    # Tabela B.2 -- P_B (medidas de proteção contra danos físicos)
    NivelProtecao.nenhum: "Estrutura não protegida por SPDA",
    NivelProtecao.IV: "Estrutura protegida por SPDA nível IV",
    NivelProtecao.III: "Estrutura protegida por SPDA nível III",
    NivelProtecao.II: "Estrutura protegida por SPDA nível II",
    NivelProtecao.I: "Estrutura protegida por SPDA nível I",
    NivelProtecao.I_descida_natural: "SPDA nível I com estrutura metálica/concreto armado como descida natural",
    NivelProtecao.captacao_descida_natural: "Cobertura metálica como captação natural + descida natural",
    # Tabelas B.3 / B.7 -- nível do DPS (P_SPD, P_EB)
    NivelDPS.IV: "DPS projetado para NP IV",
    NivelDPS.III: "DPS projetado para NP III",
    NivelDPS.II: "DPS projetado para NP II",
    NivelDPS.I: "DPS projetado para NP I",
    NivelDPS.melhor_I: "DPS com caracteristicas melhores que NP I",
    # Tabela C.3 -- fator de redução r_t (superfície do solo/piso)
    TipoSuperficie.terra_concreto: "Agricultura, concreto",
    TipoSuperficie.marmore_ceramica: "Mármore, cerâmica",
    TipoSuperficie.brita_carpete: "Cascalho, tapete, carpete",
    TipoSuperficie.asfalto_madeira: "Asfalto, linóleo, madeira",
    # Tabela C.5 -- fator de redução r_f (risco de incêndio)
    RiscoIncendio.alto: "Incêndio — risco alto",
    RiscoIncendio.normal: "Incêndio — risco normal",
    RiscoIncendio.baixo: "Incêndio — risco baixo",
    RiscoIncendio.sem_risco: "Sem risco de incêndio",
    # Tabela C.5 -- fator de redução r_f (risco de explosão)
    ZonaExplosao.nenhuma: "Sem risco de explosão",
    ZonaExplosao.zona_0_20: "Explosão — Zonas 0, 20 (e explosivos sólidos)",
    ZonaExplosao.zona_1_21: "Explosão — Zonas 1, 21",
    ZonaExplosao.zona_2_22: "Explosão — Zonas 2, 22",
    # Tabela C.2 -- ocupação da estrutura (L_F)
    TipoOcupacao.hospital: "Hospital",
    TipoOcupacao.hotel: "Hotel",
    TipoOcupacao.escola: "Escola",
    TipoOcupacao.edificio_civico: "Edifício cívico / escritório",
    TipoOcupacao.entretenimento: "Entretenimento público",
    TipoOcupacao.igreja: "Igreja",
    TipoOcupacao.museu: "Museu",
    TipoOcupacao.industrial: "Industrial",
    TipoOcupacao.comercial: "Comercial",
    TipoOcupacao.outros: "Outros",
    # Tabela C.4 -- fator de redução r_p (providências contra incêndio)
    ProvidenciaIncendio.nenhuma: "Nenhuma providência",
    ProvidenciaIncendio.extintor: "Providências manuais (extintores, hidrantes, alarme manual, rotas de escape)",
    ProvidenciaIncendio.fixo_automatico: "Instalações fixas automáticas (extinção ou alarme automático)",
    # Tabelas B.1 / B.6 -- proteção contra tensões de toque e passo (P_TA, P_TU)
    ProtecaoToquePasso.nenhuma: "Nenhuma medida de proteção",
    ProtecaoToquePasso.avisos: "Avisos de alerta",
    ProtecaoToquePasso.isolacao: "Isolação elétrica (ex.: 3 mm de polietileno reticulado)",
    ProtecaoToquePasso.malha_equipotencial: "Malha de equipotencialização do solo",
    ProtecaoToquePasso.descida_natural: "Estrutura metálica/concreto armado como descida natural",
    ProtecaoToquePasso.restricoes_fisicas: "Restrições físicas fixas",
    # Tabela A.2 -- fator de instalação C_I (roteamento da linha)
    InstalacaoLinha.aerea: "Aérea",
    InstalacaoLinha.enterrada: "Enterrada",
    InstalacaoLinha.enterrada_malha: "Enterrada em malha de aterramento",
    # Tabela A.3 -- fator tipo de linha C_T
    TipoLinha.bt_sinal: "Linha de energia (BT) ou sinal",
    TipoLinha.at_trafo: "Linha de energia em AT (com transformador AT/BT)",
    # Tabela A.4 -- fator ambiental C_E
    AmbienteLinha.rural: "Rural",
    AmbienteLinha.suburbano: "Suburbano",
    AmbienteLinha.urbano: "Urbano",
    AmbienteLinha.urbano_alto: "Urbano com edifícios mais altos que 20 m",
    # Tabela B.4 -- fatores C_LD e C_LI (tipo de linha externa)
    TipoLinhaExterna.aerea_nao_blindada: "Linha aérea não blindada",
    TipoLinhaExterna.subterranea_nao_blindada: "Linha enterrada não blindada",
    TipoLinhaExterna.energia_neutro_multiaterrado: "Linha de energia com neutro multiaterrado",
    TipoLinhaExterna.subterranea_blindada_nao_interligada: "Linha enterrada blindada, blindagem não interligada ao barramento do equipamento",
    TipoLinhaExterna.aerea_blindada_nao_interligada: "Linha aérea blindada, blindagem não interligada ao barramento do equipamento",
    TipoLinhaExterna.blindada_interligada: "Linha blindada, blindagem interligada ao barramento do equipamento",
    TipoLinhaExterna.eletroduto_metalico: "Cabo em eletroduto/tubo metálico interligado ao barramento",
    TipoLinhaExterna.fibra_optica: "Sem linha externa (fibra óptica / sistema independente)",
    TipoLinhaExterna.interface_isolante: "Interfaces isolantes conforme ABNT NBR 5419-4",
    # Tabela B.9 -- categoria da linha (P_LI)
    CategoriaLinha.energia: "Linha de energia",
    CategoriaLinha.sinal: "Linha de sinal",
    # Tabela B.8 -- condição de blindagem/RS do cabo (P_LD)
    ClasseBlindagemRS.nao_blindada: "Não blindada ou blindagem não interligada ao barramento do equipamento",
    ClasseBlindagemRS.rs_5_20: "Blindada interligada, 5 Ω/km < RS ≤ 20 Ω/km",
    ClasseBlindagemRS.rs_1_5: "Blindada interligada, 1 Ω/km < RS ≤ 5 Ω/km",
    ClasseBlindagemRS.rs_ate_1: "Blindada interligada, RS ≤ 1 Ω/km",
    # Tabela B.5 -- fiação interna (K_S3)
    FiacaoInterna.laco_grande: "Cabo não blindado, sem cuidado no roteamento (laço ≈ 50 m²)",
    FiacaoInterna.laco_medio_25: "Cabo não blindado, evitando grandes laços (≈ 25 m²)",
    FiacaoInterna.laco_medio_10: "Cabo não blindado, evitando laços médios (≈ 10 m²)",
    FiacaoInterna.laco_pequeno: "Cabo não blindado, evitando pequenos laços (≈ 0,5 m²)",
    FiacaoInterna.blindado_conduto: "Cabo blindado ou em conduto metálico",
    # Relevância da área de captação (parte da estrutura)
    RelevanciaAD.estrutura_inteira: "Estrutura inteira",
    RelevanciaAD.parte_hmin: "Parte da estrutura (altura mínima)",
    RelevanciaAD.parte_hmax: "Parte da estrutura (altura máxima)",
    # Tabela C.6 -- fator h_z (perigo especial)
    PerigoEspecial.sem_perigo: "Sem perigo especial (h_z = 1)",
    PerigoEspecial.panico_baixo: "Baixo nível de pânico — até 2 andares e ≤ 100 pessoas (h_z = 2)",
    PerigoEspecial.panico_medio: "Nível médio de pânico — eventos com 100 a 1 000 pessoas (h_z = 5)",
    PerigoEspecial.evacuacao_dificil: "Dificuldade de evacuação — pessoas imobilizadas, hospitais (h_z = 5)",
    PerigoEspecial.panico_alto: "Alto nível de pânico — eventos com mais de 1 000 pessoas (h_z = 10)",
}


def rotulo(membro) -> str:
    """Rotulo legivel de um membro de enum (fallback para o value)."""
    if membro is None:
        return "nenhum"
    return ROTULOS.get(membro, getattr(membro, "value", str(membro)))
