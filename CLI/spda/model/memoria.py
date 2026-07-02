# spda/model/memoria.py
"""Rastro do calculo (memoria de calculo). Modelos puros (pydantic).

Cada grandeza derivada e uma Operacao: guarda os operandos (com os mesmos nomes
dos parametros das funcoes de calc/) e o resultado computado. O renderer de
memorial casa a Operacao com um molde simbolico e substitui os operandos, fechando
com o resultado gravado -- bate por construcao. Lookups de tabela usam operandos
vazios e o campo `origem` (rotulo do enum/tabela).
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class Operacao(BaseModel):
    eq: str                              # id da norma, ex "A.2" ou "Tabela A.1"
    simbolo: str                         # "N_D"
    operandos: dict[str, float] = Field(default_factory=dict)
    resultado: float = 0.0
    origem: str | None = None            # rotulo p/ lookups (enum/tabela)


def _op() -> Operacao:
    # default factory de campos Operacao (placeholder seguro antes do preenchimento)
    return Operacao(eq="", simbolo="")


class MemoriaTrecho(BaseModel):
    nome: str = "trecho"
    L_L: float = 0.0
    rho: float | None = None
    C_I: Operacao = Field(default_factory=_op)
    C_E: Operacao = Field(default_factory=_op)
    C_T: Operacao = Field(default_factory=_op)
    A_L: Operacao = Field(default_factory=_op)
    N_L: Operacao = Field(default_factory=_op)
    A_I: Operacao = Field(default_factory=_op)
    N_I: Operacao = Field(default_factory=_op)
    N_DJ: Operacao | None = None


class MemoriaLinha(BaseModel):
    nome: str = "linha"
    nivel_eb: str | None = None          # rotulo do NP do DPS de entrada (P_EB)
    uw_min: float | None = None
    C_LD: Operacao = Field(default_factory=_op)
    C_LI: Operacao = Field(default_factory=_op)
    P_LD: Operacao = Field(default_factory=_op)
    P_LI: Operacao = Field(default_factory=_op)
    P_TU: Operacao = Field(default_factory=_op)
    P_EB: Operacao = Field(default_factory=_op)
    P_U: Operacao = Field(default_factory=_op)
    P_V: Operacao = Field(default_factory=_op)
    P_W: Operacao = Field(default_factory=_op)
    P_Z: Operacao = Field(default_factory=_op)
    trechos: list[MemoriaTrecho] = Field(default_factory=list)
    N_L_total: float = 0.0
    N_I_total: float = 0.0


class MemoriaSistemaInterno(BaseModel):
    nome: str = "sistema"
    U_W: float | None = None
    dps: str | None = None               # rotulo do NP do DPS coordenado (P_SPD)
    K_S1: Operacao = Field(default_factory=_op)
    K_S2: Operacao = Field(default_factory=_op)
    K_S3: Operacao = Field(default_factory=_op)
    K_S4: Operacao = Field(default_factory=_op)
    P_SPD: Operacao = Field(default_factory=_op)
    P_MS_i: Operacao = Field(default_factory=_op)
    P_C_i: Operacao = Field(default_factory=_op)


class MemoriaZona(BaseModel):
    nome: str
    n_z: int = 0
    t_z: float = 0.0
    coefs: dict[str, Operacao] = Field(default_factory=dict)
    presenca: Operacao = Field(default_factory=_op)
    L_A: Operacao = Field(default_factory=_op)
    L_B: Operacao = Field(default_factory=_op)
    L_sis: Operacao = Field(default_factory=_op)
    L_B3: Operacao | None = None
    L4_A: Operacao | None = None
    L4_B: Operacao | None = None
    L4_sis: Operacao | None = None
    P_A: Operacao = Field(default_factory=_op)
    P_C: Operacao = Field(default_factory=_op)
    P_M: Operacao = Field(default_factory=_op)
    sistemas: list[MemoriaSistemaInterno] = Field(default_factory=list)
    # Linhas sob a zona: as probabilidades P_U/P_V/P_W/P_Z e P_LD dependem do
    # contexto da zona (sistemas internos, uw_min). Geometria/eventos da linha
    # (A_L/N_L/N_I) sao zona-independentes mas ficam aqui por coesao.
    linhas: list[MemoriaLinha] = Field(default_factory=list)
    R_A: Operacao = Field(default_factory=_op)
    R_B: Operacao = Field(default_factory=_op)
    R_C: Operacao = Field(default_factory=_op)
    R_M: Operacao = Field(default_factory=_op)
    R_U: Operacao = Field(default_factory=_op)
    R_V: Operacao = Field(default_factory=_op)
    R_W: Operacao = Field(default_factory=_op)
    R_Z: Operacao = Field(default_factory=_op)
    R_B3: Operacao | None = None
    R_V3: Operacao | None = None
    R4_total: Operacao | None = None
    F_zona: Operacao = Field(default_factory=_op)


class MemoriaEstrutura(BaseModel):
    nome: str
    entradas: dict = Field(default_factory=dict)
    # F_T da estrutura (7.3.4): 0.1 se sistemas criticos, senao 1.0; ou override.
    ft: float = 1.0
    A_D: Operacao = Field(default_factory=_op)
    C_D: Operacao = Field(default_factory=_op)
    N_D: Operacao = Field(default_factory=_op)
    A_M: Operacao = Field(default_factory=_op)
    N_M: Operacao = Field(default_factory=_op)
    zonas: list[MemoriaZona] = Field(default_factory=list)
    R1: Operacao = Field(default_factory=_op)
    R3: Operacao = Field(default_factory=_op)
    R4: Operacao = Field(default_factory=_op)
    F: Operacao = Field(default_factory=_op)
    dominantes: list[tuple[str, float]] = Field(default_factory=list)


class Memoria(BaseModel):
    projeto: str
    cidade: str = ""                     # municipio base do N_G
    identificacao: object | None = None  # Identificacao (Task 5); evita import circular
    rt: dict[str, float] = Field(default_factory=dict)
    # F_T e por estrutura (MemoriaEstrutura.ft) -- depende da criticidade (7.3.4).
    # R4: True = R_T representativo (razoes c/c_t = 1); False = Anexo D detalhado.
    r4_representativo: bool = False
    estruturas: list[MemoriaEstrutura] = Field(default_factory=list)
