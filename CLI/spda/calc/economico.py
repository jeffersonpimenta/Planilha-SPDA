"""Analise economica R4 (Anexo D.2, Secao 13.4)."""
from __future__ import annotations


def custo_perdas(R4: float, c_t: float) -> float:
    """C_L = R4 x c_t (eq. D.8; com medidas: C_RL = R'4 x c_t, eq. D.10)."""
    return R4 * c_t


def custo_medidas(C_P: float, i: float, a: float, m: float) -> float:
    """C_PM = C_P x (i + a + m) (eq. D.11).

    C_P = custo das medidas; i = taxa de juros; a = taxa de amortizacao;
    m = taxa de manutencao.
    """
    return C_P * (i + a + m)


def poupanca(C_L: float, C_PM: float, C_RL: float) -> float:
    """Valor economico anual S_M = C_L - (C_PM + C_RL) (eq. D.12)."""
    return C_L - (C_PM + C_RL)


def viabilidade(C_L: float, C_RL: float, C_PM: float) -> bool:
    """True se a protecao e justificada: S_M > 0 (D.12, estrito)."""
    return poupanca(C_L, C_PM, C_RL) > 0
