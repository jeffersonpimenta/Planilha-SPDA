from __future__ import annotations

from pydantic import BaseModel, Field

from spda.model.enums import (
    Localizacao, TipoConstrucao, NivelProtecao, NivelDPS, TipoSuperficie,
    RiscoIncendio, ProvidenciaIncendio, InstalacaoLinha, TipoLinha,
    AmbienteLinha, TipoLinhaExterna, ProtecaoToquePasso, RelevanciaAD,
    CategoriaLinha, ClasseBlindagemRS, TipoOcupacao, ZonaExplosao,
)
from spda.model.identificacao import Identificacao
from spda.model.solucao import Solucao


class Medidas(BaseModel):
    """Medidas de protecao de nivel ZONA (ajustaveis no laco)."""
    protecao_toque_passo: ProtecaoToquePasso = ProtecaoToquePasso.nenhuma


class SistemaInterno(BaseModel):
    nome: str = "sistema"
    # Tensao suportavel de impulso (kV). Alimenta K_S4 (=1/U_W) e as colunas de
    # P_LD (B.8) / P_LI (B.9). None -> P_M=1 e coluna de U_W conservadora (1 kV).
    U_W: float | None = None
    K_S1: float = 1.0
    K_S2: float = 1.0
    K_S3: float = 1.0                # via Tabela B.5 (lookup no wizard) ou direto
    K_S4: float | None = None        # override; None -> derivado de U_W (min(1, 1/U_W))
    # DPS coordenado que protege ESTE sistema interno (Papel A) -> P_SPD (Tabela B.3).
    # None -> P_SPD = 1.0 (sem DPS). Forca e dados podem ter NP distintos.
    dps: NivelDPS | None = None
    # Equipamento exposto em ZPR 0A (isolado/topo da estrutura) -> soma F_B na
    # frequencia de danos (Tabela 7, nota a).
    em_zpr0a: bool = False


class Trecho(BaseModel):
    L_L: float = Field(default=1000.0, gt=0)  # m; default se desconhecido
    rho: float | None = Field(default=None, gt=0)  # resistividade do solo (ohm*m)
    instalacao: InstalacaoLinha | None = None  # override do trecho
    ambiente: AmbienteLinha | None = None
    tipo: TipoLinha | None = None


class EstruturaAdjacente(BaseModel):
    L_J: float = Field(gt=0)
    W_J: float = Field(gt=0)
    H_J: float = Field(gt=0)
    localizacao_J: Localizacao = Localizacao.isolada


class Linha(BaseModel):
    nome: str = "linha"
    tipo: TipoLinha = TipoLinha.bt_sinal             # C_T (BT/sinal vs AT c/ trafo)
    categoria: CategoriaLinha = CategoriaLinha.energia  # energia/sinal -> P_LI (B.9)
    instalacao: InstalacaoLinha = InstalacaoLinha.aerea
    ambiente: AmbienteLinha = AmbienteLinha.rural
    tipo_externa: TipoLinhaExterna = TipoLinhaExterna.aerea_nao_blindada  # C_LD/C_LI
    classe_blindagem: ClasseBlindagemRS = ClasseBlindagemRS.nao_blindada  # P_LD (B.8)
    nivel_eb: NivelDPS | None = None    # NP do DPS de EB na entrada -> P_EB (B.7); None=1.0
    protecao_toque_entrada: ProtecaoToquePasso = ProtecaoToquePasso.nenhuma  # P_TU (B.6)
    # Estrutura adjacente conectada no extremo desta linha (Secao 9.1) -> N_DJ.
    adjacente: EstruturaAdjacente | None = None
    trechos: list[Trecho] = Field(default_factory=lambda: [Trecho()])


class Zona(BaseModel):
    nome: str
    superficie: TipoSuperficie
    n_z: int = Field(ge=0)
    t_z: float = Field(ge=0, le=8760)
    h_z: float = Field(default=1.0, ge=1.0)  # fator de perigo especial (Tabela C.6)
    relevancia_AD: RelevanciaAD = RelevanciaAD.estrutura_inteira
    # L3 (patrimonio) e L4 (economico) -- opcionais
    c_z: float | None = None
    c_a: float | None = None
    c_b: float | None = None
    c_c: float | None = None
    c_s: float | None = None
    medidas: Medidas = Field(default_factory=Medidas)
    sistemas_internos: list[SistemaInterno] = Field(default_factory=list)


class Estrutura(BaseModel):
    nome: str
    L: float = Field(gt=0)
    W: float = Field(gt=0)
    H: float = Field(gt=0)
    H_min: float | None = Field(default=None, gt=0)
    H_max: float | None = Field(default=None, gt=0)
    localizacao: Localizacao
    tipo_construcao: TipoConstrucao
    risco_incendio: RiscoIncendio
    providencias_incendio: ProvidenciaIncendio
    # Ocupacao/uso -> L_F (Tabela C.2). Default "outros" (0.01) = retrocompat.
    ocupacao: TipoOcupacao = TipoOcupacao.outros
    # Zona de atmosfera explosiva -> r_f e r_p=1 (Tabela C.5 / C.3.4).
    zona_explosao: ZonaExplosao = ZonaExplosao.nenhuma
    risco_explosao: bool = False
    sistemas_criticos: bool = False
    nivel_spda: NivelProtecao | None = None
    descida_natural: bool = False     # RESERVADO: use nivel_spda=*_descida_natural; nao aplicado no Plano 1
    c_t: float | None = None          # valor total p/ L3/L4 (patrimonio/economico)
    n_t: int = Field(gt=0)
    zonas: list[Zona] = Field(default_factory=list)
    linhas: list[Linha] = Field(default_factory=list)


class Projeto(BaseModel):
    nome: str
    cidade: str = ""                  # municipio base do N_G (tabela da norma)
    N_G: float = Field(gt=0)          # densidade de descargas (1/km2*ano)
    S_M: float | None = None          # valor economico anual em risco (R4)
    rt_override: dict[str, float] | None = None
    # Override de F_T (7.3.4: p/ sistemas criticos so autoridade pode elevar).
    ft_override: float | None = None
    # R4: metodo de avaliacao economica. False (default) = Anexo D detalhado
    # (usa as razoes c/c_t das Eqs D.1-D.4). True = R_T representativo (Tabela 4,
    # 1e-3): a nota das Eqs D.1-D.4 (norma:2635) exige razoes = 1 nesse caso.
    r4_representativo: bool = False
    estruturas: list[Estrutura] = Field(default_factory=list)
    # Overlay do Estudo de Solucoes (medidas adotadas alem das instaladas).
    # None = sem estudo salvo; arquivos antigos carregam sem migracao.
    solucao: Solucao | None = None
    identificacao: Identificacao | None = None
