"""Riscos totais R1, R3, R4 (Secao 3.2, 8.3) e comparacao com RT."""
from __future__ import annotations

from spda.model.resultado import ResultadoZona

# Componentes D3 de vida que so entram em R1 com flag explosao/critico.
_D3_VIDA = ("R_C", "R_M", "R_W", "R_Z")
_R1_BASE = ("R_A", "R_B", "R_U", "R_V")


def R1(zonas: list[ResultadoZona], incluir_d3_vida: bool) -> float:
    """R1 = soma_z (R_A+R_B+R_U+R_V [+R_C+R_M+R_W+R_Z se flag])."""
    total = 0.0
    for z in zonas:
        total += sum(getattr(z, c) for c in _R1_BASE)
        if incluir_d3_vida:
            total += sum(getattr(z, c) for c in _D3_VIDA)
    return total


def R3(zonas: list[ResultadoZona]) -> float:
    """R3 = soma_z (R_B3 + R_V3)."""
    return sum(z.R_B3 + z.R_V3 for z in zonas)


def R4(zonas: list[ResultadoZona]) -> float:
    """R4 = soma_z R4_total (economico)."""
    return sum(z.R4_total for z in zonas)


def excede(R: float, RT: float) -> bool:
    return R > RT


def dominantes_R1(zonas: list[ResultadoZona],
                  incluir_d3_vida: bool) -> list[tuple[str, float]]:
    """Soma cada componente sobre as zonas e ordena decrescente."""
    comps = list(_R1_BASE) + (list(_D3_VIDA) if incluir_d3_vida else [])
    agregado = {c: sum(getattr(z, c) for z in zonas) for c in comps}
    return sorted(agregado.items(), key=lambda kv: kv[1], reverse=True)
