"""Anexo A -- numero medio anual de eventos perigosos."""
from __future__ import annotations

import math


def area_AD(L: float, W: float, H: float) -> float:
    """Area de exposicao equivalente -- estrutura retangular (eq. A.1)."""
    return L * W + 2 * (3 * H) * (L + W) + math.pi * (3 * H) ** 2


def area_AD_complexa(L: float, W: float, H_min: float, H_max: float) -> float:
    """Forma complexa (A.2.1.3.2): maior entre A_D(H_min) pela eq. A.1 e a area
    da saliencia A'_D = pi*(3*H_P)^2 (eq. A.2), com H_P = H_max."""
    return max(area_AD(L, W, H_min), math.pi * (3 * H_max) ** 2)


def N_D(N_G: float, A_D: float, C_D: float) -> float:
    """Descargas na estrutura (eq. A.2)."""
    return N_G * A_D * C_D * 1e-6


def N_DJ(N_G: float, A_DJ: float, C_DJ: float, C_T: float) -> float:
    """Descargas na estrutura adjacente conectada pela linha (eq. A.4).

    C_T = fator de transformador AT/BT da linha conectora (Tabela A.3).
    """
    return N_G * A_DJ * C_DJ * C_T * 1e-6


def area_AM(L: float, W: float) -> float:
    """Area ate 500 m do perimetro (eq. A.6)."""
    return 2 * 500 * (L + W) + math.pi * 500 ** 2


def N_M(N_G: float, A_M: float) -> float:
    """Descargas proximo da estrutura (eq. A.5)."""
    return N_G * A_M * 1e-6


def area_AL(L_L: float, rho: float | None = None) -> float:
    """Area de captacao da linha (eq. A.8). Solo rho>400 ohm*m: forma alternativa."""
    if rho is not None and rho > 400:
        return 0.6 * math.sqrt(rho) * L_L
    return 40 * L_L


def N_L(N_G: float, A_L: float, C_I: float, C_E: float, C_T: float) -> float:
    """Descargas na linha (eq. A.7)."""
    return N_G * A_L * C_I * C_E * C_T * 1e-6


def area_AI(L_L: float) -> float:
    """Area proximo da linha (eq. A.10)."""
    return 4000 * L_L


def N_I(N_G: float, A_I: float, C_I: float, C_E: float, C_T: float) -> float:
    """Descargas proximo da linha (eq. A.9)."""
    return N_G * A_I * C_I * C_E * C_T * 1e-6
