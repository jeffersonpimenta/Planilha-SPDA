"""Anexo C/D -- quantidades relativas de perda (L1, L3, L4)."""
from __future__ import annotations

_HORAS_ANO = 8760.0


def _presenca(n_z: int, n_t: int, t_z: float) -> float:
    if n_t == 0:
        return 0.0
    return (n_z / n_t) * (t_z / _HORAS_ANO)


def L_choque(r_t: float, L_T: float, n_z: int, n_t: int, t_z: float,
             r_s: float) -> float:
    """D1 -- L_A / L_U (eq. C.1/C.2)."""
    return r_t * L_T * _presenca(n_z, n_t, t_z) * r_s


def L_fisico(r_p: float, r_f: float, h_z: float, L_F: float, n_z: int,
             n_t: int, t_z: float, r_s: float) -> float:
    """D2 -- L_B / L_V (eq. C.3)."""
    return r_p * r_f * h_z * L_F * _presenca(n_z, n_t, t_z) * r_s


def L_sistemas(L_O: float, n_z: int, n_t: int, t_z: float, r_s: float) -> float:
    """D3 -- L_C / L_M / L_W / L_Z (eq. C.4)."""
    return L_O * _presenca(n_z, n_t, t_z) * r_s


def L3_patrimonio(r_p: float, r_f: float, L_F: float, c_z: float,
                  c_t: float) -> float:
    """L3 -- patrimonio cultural (eq. C.7): r_p*r_f*L_F*(c_z/c_t), limitada a 1."""
    if c_t == 0:
        return 0.0
    return min(1.0, r_p * r_f * L_F * (c_z / c_t))


# Nota das Eqs D.1-D.4 (norma:2635): as razoes c/c_t so entram na analise
# detalhada do Anexo D. Com R_T representativo (Tabela 4), as razoes viram 1.

def L4_choque(r_t: float, L_T: float, c_a: float = 0.0, c_t: float = 0.0,
              representativo: bool = False, animais: bool = True) -> float:
    """L4 D1 (eq. D.1): r_t*L_T*(c_a/c_t). representativo -> razao = 1.

    Tabela C.12: L_T so se aplica onde ha animais. No modo detalhado c_a = 0 ja
    zera D1; no representativo a razao vira 1, entao `animais=False` zera.
    """
    if representativo:
        return r_t * L_T if animais else 0.0
    return r_t * L_T * (c_a / c_t) if c_t else 0.0


def L4_fisico(r_p: float, r_f: float, L_F: float, c_a: float = 0.0,
              c_b: float = 0.0, c_c: float = 0.0, c_s: float = 0.0,
              c_t: float = 0.0, representativo: bool = False) -> float:
    """L4 D2 (eq. D.3): r_p*r_f*L_F*(c_a+c_b+c_c+c_s)/c_t. representativo -> 1."""
    if representativo:
        return r_p * r_f * L_F
    return r_p * r_f * L_F * (c_a + c_b + c_c + c_s) / c_t if c_t else 0.0


def L4_sistemas(L_O: float, c_s: float = 0.0, c_t: float = 0.0,
                representativo: bool = False) -> float:
    """L4 D3 (eq. D.4): L_O*(c_s/c_t). representativo -> razao = 1."""
    if representativo:
        return L_O
    return L_O * (c_s / c_t) if c_t else 0.0
