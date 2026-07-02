# -*- coding: utf-8 -*-
"""Relatorio Markdown completo (Secao 16.3). Funcao pura: devolve str."""
from __future__ import annotations

from spda.model.resultado import Resultado, ResultadoEstrutura
from spda.solucao.estudo import EstudoSolucao

_COMPONENTES = ("R_A", "R_B", "R_C", "R_M", "R_U", "R_V", "R_W", "R_Z")


def _status(excede: bool) -> str:
    return "EXCEDE" if excede else "OK"


def _bloco_estrutura(est: ResultadoEstrutura, rt: dict) -> list[str]:
    L: list[str] = [f"## Estrutura: {est.nome}", ""]
    L.append(f"- N_D = {est.N_D:.3e}  |  N_M = {est.N_M:.3e}  |  N_DJ = {est.N_DJ:.3e}")
    L += ["", "| Risco | Valor | Tolerável | Status |", "|---|---|---|---|"]
    L.append(f"| R1 | {est.R1:.3e} | {rt['R1']:.1e} | {_status(est.excede_R1)} |")
    L.append(f"| R3 | {est.R3:.3e} | {rt['R3']:.1e} | {_status(est.excede_R3)} |")
    L.append(f"| R4 | {est.R4:.3e} | {rt['R4']:.1e} | {_status(est.excede_R4)} |")
    L.append(f"| F  | {est.F:.3e} | {est.ft:.1e} | {_status(est.excede_F)} |")
    L += ["", "**Componentes dominantes (R1):**", ""]
    for nome, val in est.dominantes:
        L.append(f"- {nome} = {val:.3e}")
    L += ["", "**Componentes por zona:**", ""]
    cab = "| Zona | " + " | ".join(_COMPONENTES) + " |"
    sep = "|---" * (len(_COMPONENTES) + 1) + "|"
    L += [cab, sep]
    for z in est.zonas:
        vals = " | ".join(f"{getattr(z, c):.2e}" for c in _COMPONENTES)
        L.append(f"| {z.nome} | {vals} |")
    L.append("")
    return L


def _bloco_estudo(estudo: EstudoSolucao) -> list[str]:
    L: list[str] = ["## Estudo de Solução", ""]
    for e in estudo.estruturas:
        L.append(f"### {e.nome}")
        L.append(f"- R1 inicial = {e.R1_inicial:.3e}  →  R1 final = {e.R1_final:.3e}"
                 f"  (RT = {e.rt_R1:.1e})")
        L.append(f"- F inicial = {e.F_inicial:.3e}  →  F final = {e.F_final:.3e}"
                 f"  (FT = {e.ft:.1e})")
        if e.atingiu_rt and e.atingiu_ft:
            L.append("- Resultado: **R1 ≤ RT e F ≤ FT atingidos** com as medidas "
                     "abaixo.")
        else:
            L.append("- Resultado: **limites não atingidos**; reporta-se o menor "
                     "R1/F alcançável (Seção 11.1).")
        L += ["", "| # | Medida | Parâmetro | De → Para | R1 projetado "
              "| F projetado |", "|---|---|---|---|---|---|"]
        for i, p in enumerate(e.passos, 1):
            L.append(f"| {i} | {p.medida} | {p.parametro} | {p.de} → {p.para} "
                     f"| {p.R_projetado:.3e} | {p.F_projetado:.3e} |")
        L.append("")
    return L


def gerar_markdown(resultado: Resultado,
                   estudo: EstudoSolucao | None = None) -> str:
    L: list[str] = [f"# Relatório de Análise de Risco — {resultado.projeto}", ""]
    L.append("Conforme ABNT NBR 5419-2:2026.")
    L.append("")
    for est in resultado.estruturas:
        L += _bloco_estrutura(est, resultado.rt)
    if estudo is not None and estudo.estruturas:
        L += _bloco_estudo(estudo)
    return "\n".join(L)
