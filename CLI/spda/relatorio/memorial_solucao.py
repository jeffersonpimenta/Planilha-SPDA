# spda/relatorio/memorial_solucao.py
"""Memorial unico: memorial de calculo do estado instalado + secao do
Estudo de Solucoes (medidas adotadas, comparacao antes -> depois e o
recalculo do risco no estado proposto), inserida antes do glossario pelo
mesmo gerador do memorial normal.

O recalculo repete apenas o que as medidas do catalogo podem alterar:
coeficientes de zona (r_p, P_TA, P_B), perdas (r_p entra em L_B/L_V/L4),
sistemas internos (K_S2/K_S3, P_SPD, P_MS), fatores e probabilidades de
linha (C_LD/C_LI, P_LD/P_LI, P_TU, P_EB, P_U..P_Z), probabilidades
agregadas (P_A/P_C/P_M), componentes de risco e agregacao R1/R3/R4/F.
Eventos (A_D..N_I, C_I/C_E/C_T) nao dependem de nenhuma medida e ficam
so no memorial do estado instalado."""
from __future__ import annotations

from spda.app import analisar, analisar_memoria
from spda.model.projeto import Projeto
from spda.relatorio.documento import (
    Documento, Nota, Paragrafo, QuebraPagina, Tabela, Titulo, para_markdown,
)
from spda.relatorio.formato import fmt
from spda.relatorio.html import para_html
from spda.relatorio.memorial import _bloco_zona, _eq, gerar_documento
from spda.solucao.aplicar import aplicar_solucao
from spda.solucao.catalogo import MEDIDAS, por_id


def _status(excede: bool) -> str:
    return "EXCEDE" if excede else "OK"


def _bloco_recalculo(me) -> list:
    """Recalculo do risco da estrutura no estado proposto (MemoriaEstrutura
    do projeto com a solucao aplicada). Sem dados de entrada nem eventos."""
    blocos: list = [Titulo(3, f"Recálculo do risco -- {me.nome} "
                              "(estado proposto)")]
    blocos.append(Paragrafo(
        "Repetição do cálculo com as medidas adotadas: coeficientes, "
        "perdas, probabilidades de dano, componentes de risco e riscos. "
        "Números de eventos (N_D, N_M, N_L, N_I) não dependem das medidas "
        "e permanecem os do memorial acima."))
    for mz in me.zonas:
        blocos += _bloco_zona(mz, trechos=False)
    blocos.append(Titulo(4, "Agregação de riscos (estado proposto)"))
    for op in (me.R1, me.R3, me.R4, me.F):
        blocos.append(_eq(op))
    return blocos


def _bloco_comparacao(projeto: Projeto, antes, depois, avisos: list[str],
                      mem_depois=None) -> list:
    blocos: list = [QuebraPagina(),
                    Titulo(2, f"Estudo de Soluções -- {projeto.nome}")]
    for a in avisos:
        blocos.append(Nota("aviso", a))

    sol = projeto.solucao
    if sol is None or not any(se.medidas for se in sol.estruturas.values()):
        blocos.append(Nota(
            "info", "Nenhuma medida adotada: o memorial acima reflete o "
                    "estado instalado."))
        return blocos

    medidas = por_id()
    # Primeira ocorrencia vence (mesma regra de aplicar_solucao para
    # nomes repetidos).
    por_nome_antes: dict = {}
    por_nome_depois: dict = {}
    por_nome_mem: dict = {}
    originais: dict = {}
    for e in antes.estruturas:
        por_nome_antes.setdefault(e.nome, e)
    for e in depois.estruturas:
        por_nome_depois.setdefault(e.nome, e)
    for me in (mem_depois.estruturas if mem_depois is not None else []):
        por_nome_mem.setdefault(me.nome, me)
    for e in projeto.estruturas:
        originais.setdefault(e.nome, e)

    for nome, se in sol.estruturas.items():
        if nome not in originais or not se.medidas:
            continue
        est = originais[nome]
        blocos.append(Titulo(3, f"Estrutura: {nome} -- medidas adotadas"))
        linhas = []
        for mid, degrau in se.medidas.items():
            m = medidas.get(mid)
            if m is None:
                continue
            alvo = m.indice_de_degrau_str(degrau)
            adotado = m.rotulo_degrau(alvo) if alvo is not None else degrau
            linhas.append([m.descricao, m.parametro, m.nivel_atual(est),
                           adotado, ", ".join(m.componentes)])
        blocos.append(Tabela(
            ["Medida", "Parâmetro", "Instalado", "Adotado", "Componentes"],
            linhas))

        ra, rd = por_nome_antes[nome], por_nome_depois[nome]
        blocos.append(Paragrafo(
            f"R1: {fmt(ra.R1)} (antes, {_status(ra.excede_R1)}) -> "
            f"{fmt(rd.R1)} (depois, {_status(rd.excede_R1)}); "
            f"RT = {fmt(antes.rt['R1'])}. "
            f"F: {fmt(ra.F)} (antes, {_status(ra.excede_F)}) -> "
            f"{fmt(rd.F)} (depois, {_status(rd.excede_F)}); "
            f"FT = {fmt(ra.ft)}."))

        travadas = [m.descricao for m in MEDIDAS
                    if m.indice_atual(est) is None]
        if travadas:
            blocos.append(Paragrafo(
                "Medidas não avançáveis nesta estrutura (valor fora da "
                "escada discreta ou sem elemento aplicável): "
                + "; ".join(travadas) + "."))

        if nome in por_nome_mem:
            blocos += _bloco_recalculo(por_nome_mem[nome])
    return blocos


def gerar_documento_solucao(projeto: Projeto,
                            config: str | None = None) -> Documento:
    antes = analisar(projeto, config)
    aplicado, avisos = aplicar_solucao(projeto)
    depois = analisar(aplicado, config)
    # Memorial do estado INSTALADO; a secao de solucao (comparacao +
    # recalculo do estado proposto) entra antes do glossario.
    memoria = analisar_memoria(projeto, config)
    mem_depois = analisar_memoria(aplicado, config)
    sol = _bloco_comparacao(projeto, antes, depois, avisos, mem_depois)
    return gerar_documento(memoria, solucao=sol)


def gerar_memorial_solucao_markdown(projeto: Projeto,
                                    config: str | None = None) -> str:
    return para_markdown(gerar_documento_solucao(projeto, config))


def gerar_memorial_solucao_html(projeto: Projeto,
                                config: str | None = None) -> str:
    return para_html(gerar_documento_solucao(projeto, config),
                     titulo=f"Análise de Risco -- {projeto.nome}")
