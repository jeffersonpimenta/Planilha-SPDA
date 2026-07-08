# spda/relatorio/diagnostico.py
"""Diagnostico narrativo por estrutura.

Traduz os numeros da Memoria em texto corrido: veredito de adequacao por R1 e
componentes dominantes com sugestao de onde atuar. Puro (Titulo/Paragrafo).
"""
from __future__ import annotations

from spda.calc import riscos
from spda.model.memoria import Memoria, MemoriaEstrutura
from spda.relatorio.documento import Paragrafo, Titulo
from spda.relatorio.formato import fmt

# Onde atuar para reduzir cada componente dominante de R1.
_INTERVENCAO = {
    "R_A": "proteção contra tensão de toque e passo (P_TA)",
    "R_U": "DPS de equipotencialização na entrada e proteção de toque (P_U)",
    "R_B": "SPDA e medidas contra incêndio (P_B, r_p)",
    "R_V": "SPDA, DPS de entrada e medidas contra incêndio (P_V)",
    "R_C": "DPS coordenado e blindagem dos sistemas internos (P_C)",
    "R_M": "blindagem espacial e DPS dos sistemas internos (P_M)",
    "R_W": "DPS coordenado na linha e blindagem (P_W)",
    "R_Z": "blindagem interna e DPS dos sistemas (P_Z)",
}


def _narrativa_estrutura(me: MemoriaEstrutura, mem: Memoria) -> list:
    veredito = "INADEQUADA" if riscos.excede(me.R1.resultado, mem.rt["R1"]) \
        else "ADEQUADA"
    blocos = [
        Titulo(3, me.nome),
        Paragrafo(
            f"A estrutura **{me.nome}** apresenta R1 = {fmt(me.R1.resultado)} "
            f"contra o limite RT = {fmt(mem.rt['R1'])}, sendo considerada "
            f"**{veredito}** quanto ao risco de vida (R1)."),
    ]
    if me.dominantes:
        principal = me.dominantes[0][0]
        onde = _INTERVENCAO.get(principal, "as medidas de proteção aplicáveis")
        itens = "; ".join(f"{nome} = {fmt(val)}" for nome, val in me.dominantes)
        blocos.append(Paragrafo(
            f"Componentes dominantes de R1: {itens}. Para reduzir R1, "
            f"recomenda-se atuar prioritariamente sobre {onde}."))
    return blocos


def gerar_diagnostico(mem: Memoria) -> list:
    blocos: list = [Titulo(2, "Diagnóstico por estrutura")]
    for me in mem.estruturas:
        blocos += _narrativa_estrutura(me, mem)
    return blocos
