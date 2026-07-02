"""Componentes de risco R_x = N * P * L (eq. 3-11) e somatorio de trechos (Secao 9)."""
from __future__ import annotations


def componente(N: float, P: float, L: float) -> float:
    """R_x generico (eq. 3). Usado por R_A, R_B, R_C, R_M, R_Z."""
    return N * P * L


def R_linha(trechos: list[tuple[float, float]], P: float, L: float) -> float:
    """Componentes de linha (R_U, R_V, R_W) somados por trecho.

    `trechos`: lista de (N_evento, N_DJ) por trecho. Para R_U/R_V/R_W,
    N_evento = N_L do trecho; para R_Z, usar `componente` com N_I por trecho.
    """
    return sum((N + N_DJ) * P * L for (N, N_DJ) in trechos)
