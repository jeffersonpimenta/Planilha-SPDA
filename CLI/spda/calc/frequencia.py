"""Frequencia de danos F (Secao 7, Tabela 7). Funcoes puras."""
from __future__ import annotations


def F_B(N_D: float, P_B: float) -> float:
    """Equip. isolado em ZPR0A, no topo da estrutura."""
    return N_D * P_B


def F_C(N_D: float, P_C: float) -> float:
    return N_D * P_C


def F_M(N_M: float, P_M: float) -> float:
    return N_M * P_M


def F_V(N_L_total: float, P_EB: float) -> float:
    """Tabela 7: F_V = (N_L + N_DJ) x P_EB (S3, corrente impulsiva direta).

    N_L_total = (N_L + N_DJ) acumulado da linha. A guarda contra a corrente
    direta injetada e a ligacao equipotencial de entrada (P_EB), nao P_V.
    """
    return N_L_total * P_EB


def F_W(N_L_total: float, P_W: float) -> float:
    """Tabela 7: F_W = (N_L + N_DJ) x P_W (S3, corrente induzida)."""
    return N_L_total * P_W


def F_Z(N_I_total: float, P_Z: float) -> float:
    return N_I_total * P_Z


def F_zona(F_C: float, F_M: float, F_V: float, F_W: float, F_Z: float,
           F_B: float = 0.0) -> float:
    """F da zona (7.4.3). F_B so quando ha equipamento em ZPR 0A (Tabela 7-a)."""
    return F_B + F_C + F_M + F_V + F_W + F_Z
