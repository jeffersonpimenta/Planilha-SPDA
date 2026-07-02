"""Resumo no terminal. linhas_resumo() e pura; imprimir_resumo() usa rich."""
from __future__ import annotations

from spda.model.resultado import Resultado


def linhas_resumo(resultado: Resultado) -> list[dict]:
    """Uma linha por estrutura, com R/RT/F e status (puro, testavel)."""
    out: list[dict] = []
    rt = resultado.rt
    for est in resultado.estruturas:
        out.append({
            "estrutura": est.nome,
            "R1": est.R1, "status_R1": "EXCEDE" if est.excede_R1 else "OK",
            "R3": est.R3, "status_R3": "EXCEDE" if est.excede_R3 else "OK",
            "R4": est.R4, "status_R4": "EXCEDE" if est.excede_R4 else "OK",
            "F": est.F, "status_F": "EXCEDE" if est.excede_F else "OK",
            "rt": rt, "ft": est.ft,
        })
    return out


def imprimir_resumo(resultado: Resultado, console=None) -> None:
    """Renderiza tabela-resumo com rich."""
    from rich.console import Console
    from rich.table import Table

    console = console or Console()
    tabela = Table(title=f"Análise de Risco — {resultado.projeto}")
    for col in ("Estrutura", "R1", "R3", "R4", "F"):
        tabela.add_column(col)

    def cel(valor: float, status: str) -> str:
        cor = "red" if status == "EXCEDE" else "green"
        return f"[{cor}]{valor:.2e} ({status})[/{cor}]"

    for ln in linhas_resumo(resultado):
        tabela.add_row(
            ln["estrutura"],
            cel(ln["R1"], ln["status_R1"]),
            cel(ln["R3"], ln["status_R3"]),
            cel(ln["R4"], ln["status_R4"]),
            cel(ln["F"], ln["status_F"]),
        )
    console.print(tabela)
