"""Anexo B -- probabilidades de dano. Funcoes puras sobre fatores ja resolvidos."""
from __future__ import annotations

from functools import reduce


def P_A(P_TA: float, P_B: float) -> float:        # eq. B.1
    return P_TA * P_B


def P_C(P_SPD: float, C_LD: float) -> float:      # eq. B.2
    return P_SPD * C_LD


def P_MS(K_S1: float, K_S2: float, K_S3: float, K_S4: float) -> float:  # eq. B.4
    return (K_S1 * K_S2 * K_S3 * K_S4) ** 2


def fator_KS4(U_W: float) -> float:               # K_S4 = 1/U_W (cap 1.0)
    """Fator da tensao suportavel de impulso. U_W em kV; limitado a 1.0."""
    return min(1.0, 1.0 / U_W)


def P_U(P_TU: float, P_EB: float, P_LD: float, C_LD: float) -> float:   # eq. B.8
    return P_TU * P_EB * P_LD * C_LD


def P_V(P_EB: float, P_LD: float, C_LD: float) -> float:   # eq. B.9: PV = PEB*PLD*CLD
    return P_EB * P_LD * C_LD


def P_W(P_SPD: float, P_LD: float, C_LD: float) -> float:   # eq. B.10
    return P_SPD * P_LD * C_LD


def P_Z(P_SPD: float, P_LI: float, C_LI: float) -> float:   # eq. B.11
    return P_SPD * P_LI * C_LI


def combinar_sistemas(probs: list[float]) -> float:
    """1 - produto(1 - p_i) (eq. 12/13/17/18). SO para R_C/R_M e F_C/F_M.

    Lista vazia -> 0.0.
    """
    if not probs:
        return 0.0
    return 1 - reduce(lambda acc, p: acc * (1 - p), probs, 1.0)


def pior_caso(probs: list[float]) -> float:
    """Valor unico mais restritivo (o maior) sobre os sistemas internos.

    Norma 6.9.1.2a (risco) e 7.4.1.2a (frequencia): para R_W/R_Z e F_W/F_Z
    NAO se combina sobre sistemas -- fixa-se um unico valor, o mais restritivo.
    Lista vazia -> 0.0.
    """
    return max(probs) if probs else 0.0
