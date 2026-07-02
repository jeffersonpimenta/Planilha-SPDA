from __future__ import annotations

from pydantic import BaseModel, Field


class ResultadoZona(BaseModel):
    nome: str
    # componentes de risco por tipo de perda (R1)
    R_A: float = 0.0
    R_B: float = 0.0
    R_C: float = 0.0
    R_M: float = 0.0
    R_U: float = 0.0
    R_V: float = 0.0
    R_W: float = 0.0
    R_Z: float = 0.0
    # contribuicoes L3 e L4
    R_B3: float = 0.0
    R_V3: float = 0.0
    R4_total: float = 0.0
    # frequencia de danos
    F_zona: float = 0.0


class ResultadoEstrutura(BaseModel):
    nome: str
    N_D: float = 0.0
    N_M: float = 0.0
    N_DJ: float = 0.0
    R1: float = 0.0
    R3: float = 0.0
    R4: float = 0.0
    F: float = 0.0
    # F_T da estrutura (7.3.4): 0.1 (criticos) / 1.0 (nao criticos) / override.
    ft: float = 1.0
    excede_R1: bool = False
    excede_R3: bool = False
    excede_R4: bool = False
    excede_F: bool = False
    dominantes: list[tuple[str, float]] = Field(default_factory=list)
    zonas: list[ResultadoZona] = Field(default_factory=list)


class Resultado(BaseModel):
    projeto: str
    rt: dict[str, float] = Field(default_factory=dict)
    # F_T e por estrutura (ResultadoEstrutura.ft) -- criticidade (7.3.4).
    estruturas: list[ResultadoEstrutura] = Field(default_factory=list)
