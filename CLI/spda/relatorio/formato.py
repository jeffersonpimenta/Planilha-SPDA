# spda/relatorio/formato.py
"""Formatacao numerica unica do relatorio e substituicao de operandos.

`fmt` da a representacao canonica de um numero em todo o memorial. `substituir`
troca nomes de operandos por seus valores formatados numa forma simbolica, com
limites de palavra (nao confunde C_LD com C_LI) e numa unica passada (nao
re-substitui texto ja trocado).
"""
from __future__ import annotations

import re


def fmt(x: float) -> str:
    """Numero legivel: cientifico para |x|<1e-3 ou >=1e4; senao decimal enxuto."""
    if x == 0:
        return "0"
    ax = abs(x)
    if ax < 1e-3 or ax >= 1e4:
        return f"{x:.3e}"
    return f"{x:.4g}"


def substituir(forma: str, operandos: dict[str, float]) -> str:
    """Troca cada nome de operando pela `fmt` do seu valor (limite de palavra)."""
    if not operandos:
        return forma
    nomes = sorted(operandos, key=len, reverse=True)
    padrao = re.compile(r"\b(" + "|".join(re.escape(n) for n in nomes) + r")\b")
    return padrao.sub(lambda m: fmt(operandos[m.group(1)]), forma)
